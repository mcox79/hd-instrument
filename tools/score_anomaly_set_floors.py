"""Run the F5 evaluation's MANDATORY FLOORS on the anomaly set -- **BEFORE F5 EXISTS.**

**WHY THIS IS THE RIGHT THING TO RUN FIRST.** `notes/F5_EVALUATION_DESIGN_...md` pre-committed the
kill condition: *"If plain co-occurrence surprisal finds the anomaly as well, F5 adds nothing -- and
this is the floor most likely to win."* **Counting has beaten every arm this project has built, by
roughly ten to one.** So the floor is measurable now, with no F5, and it sets the bar the organ
would have to clear. *This is "could this experiment have succeeded?" -- the highest-yield habit
found this week -- asked BEFORE the build instead of after it.*

**THE READ-OUT.** For each item, score every content position in the sentence and report **the RANK
of the anomalous position**. Rank 1 = the floor put the anomaly first. Via `tools/rank_with_ties.py`,
so both tie conventions print and no bare rank can escape -- a strict-inequality rank over a score
column with mass on one value counts every tie as beaten, which has produced three false results in
this project already.

**WHAT A LOW FLOOR RANK MEANS: F5 IS NOT WORTH BUILDING FOR THIS TASK.** That is a real finding and
it is CHEAPER TO GET NOW than after the organ exists.

**THE 17 WEAK ITEMS ARE EXCLUDED FROM THE HEADLINE AND REPORTED SEPARATELY.** They have no anomaly
to find (hand-scored), so including them would penalise every arm equally and muddy the comparison.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SET = os.environ.get("DIAG_SET",
                     os.path.join(_REPO, "data", "anomaly_set_frequency_matched_v8.json"))
HAND = SET.replace(".json", "_handscores.json")
# ALL_ITEMS: score every item rather than only the hand-scored CLEAN ones. Required for REPLICATION
# across independently-built sets, which have no hand-scores -- the WEAK items dilute every arm
# EQUALLY, so a DELTA computed the same way on every set is still comparable across sets. It is NOT
# comparable to the CLEAN-only headline, and the two are never printed as one number.
ALL_ITEMS = os.environ.get("DIAG_ALL_ITEMS", "0") == "1" or not os.path.exists(HAND)
EMIT = os.environ.get("DIAG_EMIT_DELTAS", "")
N_SENT = int(os.environ.get("DIAG_N_SENT", "8000"))
CORPUS = os.environ.get("DIAG_CORPUS", "simplewiki")


def main():
    from rank_with_ties import format_arms, rank_with_ties

    from hdlab.corpus_registry import CorpusRegistry
    from hdlab.reading_grounding_loop import content_lemmas

    print("SET: %s" % os.path.basename(SET))
    items = json.load(open(SET, encoding="utf-8"))["items"]
    if ALL_ITEMS:
        verdict = {n: "CLEAN" for n in range(len(items))}
        print("ALL-ITEMS MODE (no hand-scores for this set): every item scored. **Comparable across "
              "sets scored the same way; NOT comparable to the hand-scored CLEAN-only headline.**")
    else:
        verdict = {v["index"]: v["verdict"]
                   for v in json.load(open(HAND, encoding="utf-8"))["verdicts"]}
    clean = [(n, it) for n, it in enumerate(items) if verdict[n] == "CLEAN"]
    weak = [(n, it) for n, it in enumerate(items) if verdict[n] == "WEAK"]
    print("items: %d scored (headline), %d WEAK (reported separately), %d BROKEN (excluded)"
          % (len(clean), len(weak), sum(1 for v in verdict.values() if v == "BROKEN")))

    # ---- corpus statistics: the SAME 8,000 sentences the set was built from
    reg = CorpusRegistry()
    h = reg.handles[CORPUS]
    sents = list(h.take(N_SENT))
    # *** LEAK CONTROL, AND IT IS NOT OPTIONAL. *** The items were DRAWN FROM these same sentences,
    # so a co-occurrence table built over all of them has READ EACH ITEM'S ORIGINAL SENTENCE. It
    # would then "know" that the correct word co-occurs with its context **because it saw that exact
    # sentence**, inflating the floor and setting an unfairly high bar for the organ. *Same class as
    # the held-out split that overlapped its training pool 600/600 -- and the same fix: exclude, and
    # PRINT THE COUNT, because a control that excludes nothing is not a control.*
    held = {it["sentence_original"] for it in items}
    kept = [s for s in sents if s not in held]
    print("LEAK CONTROL: %d of %d corpus sentences removed because they ARE the item sentences "
          "(%d remain)" % (len(sents) - len(kept), len(sents), len(kept)))
    if len(sents) - len(kept) == 0:
        print("  !! the exclusion removed NOTHING -- that is a broken control, not a clean one")
    docfreq, cooc, ndoc = collections.Counter(), collections.defaultdict(collections.Counter), 0
    for s in kept:
        u = set(content_lemmas(s))
        ndoc += 1
        docfreq.update(u)
        for w in u:
            cooc[w].update(u)
    print("corpus stats over %d sentences, %d vocabulary" % (ndoc, len(docfreq)))

    def pmi_fit(w, context):
        """Mean positive PMI of `w` with the sentence's OTHER content words. THE FLOOR THAT MATTERS:
        pure counting, no representation, no learning."""
        others = [c for c in context if c != w]
        if not others:
            return 0.0
        pw = docfreq[w] / ndoc
        vals = []
        for c in others:
            pc, pjoint = docfreq[c] / ndoc, cooc[w][c] / ndoc
            if pw <= 0 or pc <= 0:
                continue
            vals.append(math.log(pjoint / (pw * pc)) if pjoint > 0 else -8.0)
        return float(np.mean(vals)) if vals else 0.0

    def orth(w, context):
        """Mean character-trigram overlap with the rest of the sentence. TIE MASS IS REPORTED --
        measured at 0.90-0.98 in three cells, where it is an accounting convention not a
        measurement."""
        def tri(x):
            x = "^" + x + "$"
            return {x[i:i + 3] for i in range(max(1, len(x) - 2))}
        tw, out = tri(w), []
        for c in context:
            if c == w:
                continue
            tc = tri(c)
            out.append(len(tw & tc) / max(1, len(tw | tc)))
        return float(np.mean(out)) if out else 0.0

    ARMS = {
        # HIGHER score = MORE anomalous, so each arm is signed to make the anomaly rank 1st
        "CO_OCCURRENCE_SURPRISAL": lambda w, ctx, pos, n: -pmi_fit(w, ctx),
        "FREQUENCY (flag the rarest)": lambda w, ctx, pos, n: -math.log(
            max(1, docfreq[w]) / ndoc),
        "ORTHOGRAPHIC": lambda w, ctx, pos, n: -orth(w, ctx),
        "POSITION (flag the last)": lambda w, ctx, pos, n: pos / max(1, n - 1),
        "LENGTH (flag the longest)": lambda w, ctx, pos, n: float(len(w)),
        "CONSTANT (query-blind)": lambda w, ctx, pos, n: 0.0,
    }

    def score_group(group, field="sentence_anomalous"):
        """`field="sentence_original"` scores the UNTOUCHED sentence at the SAME slot -- the
        decisive control: the word there is CORRECT, so an arm that still ranks it top is
        responding to the SLOT rather than to the anomaly."""
        res = {a: [] for a in ARMS}
        for _, it in group:
            toks = it[field].split()
            # candidate positions = content words the corpus knows, incl. the anomaly
            cand = [j for j, t in enumerate(toks)
                    if "".join(ch for ch in t.lower() if ch.isalpha()) in docfreq]
            if it["anomaly_token_index"] not in cand:
                cand.append(it["anomaly_token_index"])
            cand = sorted(set(cand))
            if len(cand) < 3:
                continue
            words = ["".join(ch for ch in toks[j].lower() if ch.isalpha()) for j in cand]
            tgt = cand.index(it["anomaly_token_index"])
            for a, fn in ARMS.items():
                scores = [fn(w, words, j, len(toks)) for w, j in zip(words, cand)]
                res[a].append(rank_with_ties(scores, tgt))
        return res

    print("\n" + "=" * 90)
    print("HEADLINE -- %d CLEAN items. Rank of the ANOMALOUS word among the sentence's content" %
          len(clean))
    print("words. RANK 1 = the floor found it. Lower is better; chance is ~half the candidates.")
    print("=" * 90)
    res = score_group(clean)
    print(format_arms(res))
    ncand = float(np.mean([r.pessimistic for r in res["CONSTANT (query-blind)"]]))
    print("\nCONSTANT is the information-free arm: every candidate ties, so its OPTIMISTIC rank is")
    print("1.0 by construction and its PESSIMISTIC rank (%.1f) is the candidate count. **ANY ARM"
          % ncand)
    print("WHOSE OPTIMISTIC RANK APPROACHES 1.0 WHILE ITS PESSIMISTIC RANK IS LARGE IS TIE-DEGENERATE,")
    print("NOT ACCURATE** -- that is the failure that produced three false results in this project.")

    print("\n" + "=" * 90)
    print("*** THE DECISIVE CONTROL: THE SAME FLOORS ON THE ORIGINAL, UNMODIFIED SENTENCES,")
    print("SCORED AT THE SAME SLOT. The original word is CORRECT there -- so an arm that ranks it")
    print("JUST AS HIGH is detecting THE SLOT, NOT THE ANOMALY, and carries ZERO anomaly signal.")
    print("=" * 90)
    ctrl = score_group(clean, field="sentence_original")
    print(format_arms(ctrl))
    print("")
    print("%-28s %10s %10s %10s" % ("arm", "ANOM mid", "ORIG mid", "DELTA"))
    print("-" * 62)
    rows = []
    for a in ARMS:
        if not res[a] or not ctrl[a]:
            continue
        ma = float(np.median([r.midpoint for r in res[a]]))
        mo = float(np.median([r.midpoint for r in ctrl[a]]))
        rows.append((mo - ma, a, ma, mo))
    for d, a, ma, mo in sorted(rows, reverse=True):
        tag = "  <- NO ANOMALY SIGNAL" if d <= 0.25 else ""
        print("%-28s %10.2f %10.2f %+10.2f%s" % (a, ma, mo, d, tag))
    print("")
    if EMIT:
        json.dump({"set": os.path.basename(SET), "all_items": ALL_ITEMS, "n": len(clean),
                   "deltas": {a: d for d, a, _, _ in rows}},
                  open(EMIT, "w", encoding="utf-8"), indent=1)
        print("[deltas -> %s]" % EMIT)
    print("DELTA = how much WORSE the arm ranks the CORRECT word than the intruder.")
    print("A DELTA NEAR ZERO MEANS THE ARM WOULD SCORE THE UNTOUCHED SENTENCE THE SAME WAY.")
    print("")
    print("=" * 90)
    print("THE 17 WEAK ITEMS, SEPARATELY -- hand-scored as having NO anomaly to find.")
    print("If an arm scores these as WELL as the clean ones, it is not detecting anomaly at all.")
    print("=" * 90)
    print(format_arms(score_group(weak)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
