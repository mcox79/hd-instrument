"""The grounded channel BEATS chance where the frequency prior structurally cannot -- and combining
them DESTROYS that. Both facts live in the submission's own metrics; neither is in its headline.

WHERE THIS COMES FROM. Reviewing the priority-1 solver submission (`reader_meaning_channel`,
status REFUTED, 2026-08-23). Its headline is correct as stated and its re-verify passes: the
grounded hub combined with a sense-frequency prior does NOT clear that prior's floor
(0.4702 vs 0.4778, not CI-separated). The solver also STRENGTHENED the floor against itself,
replacing the instrument's shipped uniform mean(1/k) with the harder most-frequent-sense prior.
That is good practice and the aggregate result stands.

**BUT THE AGGREGATE IS 84% DOMINANT-SENSE ITEMS (708 of 841), AND ON THOSE THE PRIOR CANNOT LOSE.**
The interesting population is the other 133 -- items whose correct sense is NOT the most frequent
one, where a most-frequent-sense rule scores 0.0000 BY CONSTRUCTION rather than by failing. What
happens there is the opposite of the headline:

    on the 53 words / 80 trials that the grounded-coherence arm actually scored,
    subject-weighted (the submission's own scorer), chance on those same items = 0.3854:

        COH_HUB     grounded channel ALONE       0.4811   ABOVE chance
        BAYES_HUB   channel + frequency prior    0.1415   far BELOW chance
        MFS_PRIOR   frequency prior alone        0.0000   zero by construction

**THE CHANNEL IS THE ONLY ARM THAT BEATS CHANCE HERE, AND ADDING THE PRIOR TO IT COSTS 0.34 --
IT LANDS BELOW RANDOM GUESSING.** So the combination rule does not COMBINE; the prior SWAMPS.
"the grounded channel adds nothing" and "our way of mixing it with the prior destroys it" predict
identical aggregates and imply opposite next steps.

TWO MEASUREMENT DEFECTS IN THE SUBMISSION, BOTH THE SAME SHAPE, NEITHER FATAL TO ITS HEADLINE:
  1. Its witness check [5] argues "coherence helps exactly where the prior fails" and cites
     BAYES_HUB 0.0827 -- an arm that is FIVE TIMES BELOW chance on that stratum. The evidence for
     its own claim is COH_HUB, sitting unmentioned in the same table.
  2. Its stratum table compares arms at n=133 against an arm at n=80 without flagging it. The
     grounded arm scores only where the sensorimotor norms cover the word (65.5% coverage), so
     every cross-arm read in that table crosses populations. THIS TEST FIXES THAT by restricting
     every arm to the items the grounded arm actually scored.

WHY THIS IS A WITNESS AND NOT A NOTE. The finding is a comparison that is only valid on one
specific subpopulation with one specific scorer. Written as prose it would be quoted without its
denominator within a day -- this project has six retractions of exactly that shape. Written here,
the numbers are recomputed from the saved population every run and the assertions fail if the
relationship changes.

NOT ESTABLISHED, AND DO NOT LET THIS TRAVEL AS IF IT WERE: 53 words is small, no CI is computed
here, and COH_HUB's advantage is measured only where its norms cover the word -- coverage is not
random, so this is NOT evidence that the channel would beat chance on the words it cannot score.
The claim is exactly: on items it can score, the channel carries subordinate-sense signal that
the combination rule then destroys.

    .venv/Scripts/python.exe verification/test_the_prior_swamps_the_grounded_channel_not_replaces_it.py
"""
import io
import json
import os
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POP = os.path.join(REPO, "data", "exp_reader_sense_selection_bayesian_hub_v1",
                   "_scored_population.json")


def subject_weighted(rows, value_of):
    """The submission's own scorer: mean over WORDS of the mean over that word's trials."""
    by_word = defaultdict(list)
    for r in rows:
        v = value_of(r)
        if v is not None:
            by_word[r["word"]].append(v)
    per_word = [sum(v) / len(v) for v in by_word.values() if v]
    return (sum(per_word) / len(per_word) if per_word else None), len(per_word)


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-62s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    if not os.path.exists(POP):
        print("[witness] FAIL the saved population is missing: %s" % POP)
        print("[witness] (the submission saved it; if it is gone the cell must be re-run)")
        raise SystemExit(1)

    with io.open(POP, encoding="utf-8") as fh:
        pop = json.load(fh)
    records = pop["records"]

    # POSITIVE CONTROL FIRST: reproduce the shipped floor from the saved population. If this
    # fails, the population and the metrics are not the same run and nothing below means anything.
    shipped_floor = 0.4316
    floor, n_words = subject_weighted(records, lambda r: 1.0 / r["k"])
    chk("the shipped uniform floor reproduces from the saved population",
        abs(floor - shipped_floor) < 0.002,
        "recomputed %.4f vs shipped %.4f over %d words" % (floor, shipped_floor, n_words))

    sub = [r for r in records if not r["dominant_congruent"]]
    chk("the aggregate is dominated by items the prior cannot lose on",
        len(sub) < 0.2 * len(records),
        "%d of %d trials (%.0f%%) are subordinate-sense" %
        (len(sub), len(records), 100.0 * len(sub) / len(records)))

    # THE SAME-POPULATION FIX: only items the grounded arm actually scored.
    scored = [r for r in sub if "COH_HUB" in r["correct"]]
    chance, n_sc = subject_weighted(scored, lambda r: 1.0 / r["k"])
    chk("restricting to what the grounded arm scored changes the denominator",
        len(scored) < len(sub),
        "%d of %d subordinate trials, %d words -- the submission compared 80 against 133"
        % (len(scored), len(sub), n_sc))

    acc = {}
    for arm in ("MFS_PRIOR", "COH_HUB", "BAYES_HUB", "BAYES_HUB_GATED"):
        v, _ = subject_weighted(scored, lambda r, a=arm: r["correct"].get(a))
        acc[arm] = v

    print("[witness] --- subordinate senses, %d words, subject-weighted, chance = %.4f ---"
          % (n_sc, chance))
    for arm in ("MFS_PRIOR", "COH_HUB", "BAYES_HUB", "BAYES_HUB_GATED"):
        print("[witness]     %-18s %.4f  %s"
              % (arm, acc[arm], "above chance" if acc[arm] > chance else "BELOW CHANCE"))

    chk("the frequency prior is zero here BY CONSTRUCTION, not by failing",
        acc["MFS_PRIOR"] == 0.0,
        "MFS_PRIOR %.4f -- a most-frequent-sense rule cannot pick a subordinate sense" % acc["MFS_PRIOR"])
    chk("the grounded channel ALONE beats chance on these items",
        acc["COH_HUB"] > chance,
        "COH_HUB %.4f vs chance %.4f (+%.4f)" % (acc["COH_HUB"], chance, acc["COH_HUB"] - chance))
    chk("adding the prior puts it BELOW chance -- the prior swamps, it does not combine",
        acc["BAYES_HUB"] < chance,
        "BAYES_HUB %.4f vs chance %.4f" % (acc["BAYES_HUB"], chance))
    chk("and that costs more than the channel's whole margin over chance",
        (acc["COH_HUB"] - acc["BAYES_HUB"]) > (acc["COH_HUB"] - chance),
        "channel %.4f -> combined %.4f, a drop of %.4f"
        % (acc["COH_HUB"], acc["BAYES_HUB"], acc["COH_HUB"] - acc["BAYES_HUB"]))
    chk("the gated variant does not rescue it either",
        acc["BAYES_HUB_GATED"] < chance,
        "BAYES_HUB_GATED %.4f" % acc["BAYES_HUB_GATED"])

    # NEGATIVE CONTROL: the same reading must NOT hold on the dominant stratum, or the effect is
    # an artifact of the restriction rather than a property of subordinate senses.
    dom = [r for r in records if r["dominant_congruent"] and "COH_HUB" in r["correct"]]
    d_acc, _ = subject_weighted(dom, lambda r: r["correct"].get("MFS_PRIOR"))
    chk("NEGATIVE CONTROL: on dominant items the prior is strong, not zero",
        d_acc is not None and d_acc > 0.3,
        "MFS_PRIOR on dominant %.4f -- so the zero above is specific to the stratum" % d_acc)

    print()
    print("[witness] READ THIS AS: the channel carries subordinate-sense signal ON THE ITEMS IT")
    print("[witness] COVERS, and the combination rule destroys it. NOT as: the channel works.")
    print("[witness] RESULT: %s" % ("ALL WITNESS CHECKS PASS" if ok else "FAILED"))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()

# ---- PYTEST ENTRY POINT ------------------------------------------------------------------
# WIRED 2026-08-23. WITHOUT THIS THE FILE IS ISLANDED: it is named test_*.py and sits in
# verification/, so it LOOKS like it is in the certification gate, but it defines no test_
# function, so pytest collects ZERO tests from it and run_certification.py never executes it.
# That is the same shape as the hazard run_certification.py documents in its own comment (a
# script-style file under a test_ name), arriving from the opposite direction: that one aborted
# the suite loudly, this one is skipped silently. A witness the gate does not run is a witness
# nobody runs.
# This reads only a metrics.json, so it costs milliseconds and is safe to add to the gate.
def test_the_prior_swamps_the_grounded_channel():
    try:
        main()
    except SystemExit as exc:
        assert exc.code == 0, "witness FAILED (exit %r) -- run the file directly for the detail" % (exc.code,)
