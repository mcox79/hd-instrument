"""Vocabulary grows with reading. Grounding precision is at the random floor. Only one is an outcome.

WHY THIS EXISTS -- IT CORRECTS A DIRECTION I WAS ABOUT TO SET. Across 2026-08-23 two measurements
looked like they converged on "reading volume is the binding constraint":

  * the learn-from-reading submission clears the strongest floor CI-separated on three banks and is
    STILL CLIMBING at 38.09M tokens (corpus-limited, not exhausted);
  * my own measurement here: the substrate's vocabulary is still climbing at 5,200 sentences
    (2,270 lemmas at 800 -> 7,334 at 5,200), nowhere near saturation.

**BOTH ARE TRUE AND THE CONCLUSION DOES NOT FOLLOW.** Vocabulary size is an INTERNAL STATISTIC. This
repo has a standing rule -- earned three times in one day on 2026-08-20 -- that a statistic the
mechanism optimises may DIAGNOSE but may never DECIDE, and that the held-out TASK wins when the two
disagree. So the question is what the substrate's grounding OUTCOME does, and it is measured:

    data/exp_substrate_resume_helps_v1  (3 seeds, 4,000-sentence matched reads)

        SUBSTRATE grounding precision   0.0199   (3 hits / 151 scorable)
        RANDOM_ANCHOR floor             0.0000
        paired permutation p             0.2634   <- NOT separated
        MOST_FREQUENT_ANCHOR floor      0.0000

**THE SUBSTRATE GROUNDS 168 MEANINGS AND THREE OF THEM ARE RIGHT, WHICH IS NOT DISTINGUISHABLE FROM
RANDOM.** Reading more would grow a vocabulary whose attached meanings are at chance. **Scaling the
input of a mechanism that performs at its floor scales nothing.**

WHY THE TWO RESULTS ARE NOT IN CONFLICT, WHICH IS THE USEFUL PART. The submission that SUCCEEDED did
not use the substrate's grounding path at all -- it built a PPMI-SVD distributional model over raw
simplewiki text. So:

    the information IS in the text          (distributional statistics extract it, CI-separated)
    the substrate does NOT extract it       (its own grounding sits at the random floor)

**THE GAP IS NOT READING VOLUME. IT IS THE EXTRACTION MECHANISM.** That reframes "read more" (which
this evidence does not support) into "find out why the substrate's grounding is at chance while a
plain distributional model over the same corpus is not" (which it does).

NOT ESTABLISHED, AND STATED SO IT CANNOT TRAVEL FURTHER THAN IT GOES:
  * n=151 scorable with 3 hits is SMALL. The claim is "not distinguishable from the floor", NOT
    "exactly zero" -- an underpowered test cannot prove absence of a small effect.
  * The precision gold is `conceptnet_gold_v1`. A different gold could score differently, and the
    submission says its coverage is 0.899.
  * Vocabulary growth and grounding precision were measured on DIFFERENT reads. This test asserts
    each against its own source and deliberately computes NO cross-quantity ratio.

    .venv/Scripts/python.exe verification/test_reading_more_does_not_follow_grounding_is_at_chance.py
"""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESUME = os.path.join(REPO, "data", "exp_substrate_resume_helps_v1", "metrics.json")


def find_precision_blocks(obj, out, path=""):
    """Walk to every arm's precision block. Enumerate rather than assume the key path -- the
    'list the fields that exist' rule, after a wrong-field guess cost a whole retracted finding."""
    if isinstance(obj, dict):
        if "SUBSTRATE" in obj and isinstance(obj.get("SUBSTRATE"), dict) \
                and "precision" in obj["SUBSTRATE"]:
            out.append((path, obj))
        for k, v in obj.items():
            find_precision_blocks(v, out, path + "/" + str(k))


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-60s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    if not os.path.exists(RESUME):
        print("[witness] FAIL missing %s" % RESUME)
        raise SystemExit(1)
    with io.open(RESUME, encoding="utf-8") as fh:
        m = json.load(fh)

    blocks = []
    find_precision_blocks(m, blocks)
    chk("found the precision blocks by enumeration, not by a guessed key path",
        len(blocks) > 0, "%d block(s)" % len(blocks))

    checked = 0
    for path, blk in blocks:
        sub = blk["SUBSTRATE"]
        if sub.get("precision") is None:      # an arm that scored nothing is not evidence
            continue
        # A floor whose precision is None is UNMEASURED, not zero. Treating a null as a zero floor
        # would silently invent the weakest possible comparator -- the exact JSON-null-read-as-a-
        # null-hypothesis error this repo has already paid for once.
        floors = {k: v for k, v in blk.items()
                  if k != "SUBSTRATE" and isinstance(v, dict)
                  and v.get("precision") is not None}
        if not floors:
            continue
        best = max(floors, key=lambda k: floors[k]["precision"])
        f = floors[best]
        p = f.get("paired_perm_p_vs_SUBSTRATE")
        print("[witness]   %s" % path.lstrip("/"))
        print("[witness]     SUBSTRATE %.4f (%s/%s)  strongest floor %s %.4f  paired p=%s"
              % (sub["precision"], sub.get("hits"), sub.get("n"), best, f["precision"], p))
        if p is not None:
            chk("grounding is NOT separated from its floor (%s)" % path.split("/")[-2][:22],
                p > 0.05,
                "p=%.4f -- %d hits in %s is not distinguishable from random"
                % (p, sub.get("hits", -1), sub.get("n", "?")))
            checked += 1

    chk("at least one arm was actually tested against its floor", checked > 0,
        "%d arm(s) carried a paired permutation p" % checked)

    print()
    print("[witness] READ AS: vocabulary growth is a STATISTIC and it is climbing; grounding")
    print("[witness] precision is the OUTCOME and it is at chance. 'Read more' does not follow.")
    print("[witness] The extraction mechanism is the gap, not the corpus.")
    print("[witness] RESULT: %s" % ("ALL WITNESS CHECKS PASS" if ok else "FAILED"))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
