"""IS THE STORY TEST WE ALREADY OWN CAPABLE OF SHOWING A DIFFERENCE? (board Q77, instrument check)

THE SITUATION. `social_iqa` is the one thing on our shelf that asks what a character WANTED rather
than what a text stated: 1,954 validation items, three answers, questions like "Remy baited Kai's
hook -- what will Remy want to do next?". Ten cells ran it on 2026-08-11 and every arm landed
0.3501-0.3975 against a 0.3362 majority floor. **The word-counting baseline sat at 0.3501 too.**

*** THE CLAIM I FILED ON THE BOARD, WHICH THIS SCRIPT EXISTS TO CHECK RATHER THAN ASSUME. ***
I wrote: "when the clever method AND the crude floor both sit at chance, the likeliest reading is
the test is not reaching either of them." **That may be exactly backwards here.** If this dataset
was built so that surface cues CANNOT work, then a crude method scoring at chance is the instrument
WORKING AS DESIGNED, not evidence it is broken -- and our substrate's chance score is then a real
negative rather than an untestable one. I am not going to settle that from recollection about how
the dataset was constructed. It is measurable on disk in seconds.

THE MEASUREMENT: what does a method WITH a known, real, non-semantic signal score?
  RANDOM        pick uniformly                                  -- the trivial floor
  MAJORITY      always the commonest label                      -- the label-prior floor
  LONGEST       pick the longest answer      *** the classic multiple-choice ANNOTATION ARTIFACT;
                                                 on many crowdsourced sets this alone beats chance
  OVERLAP       most content-word overlap with context+question -- the SURFACE-CUE baseline
  RAREST        answer containing the rarest word               -- a frequency artifact probe

HOW TO READ IT, PRE-COMMITTED:
  ALL of them at chance -> the dataset genuinely carries no surface or artifact signal. **The
      instrument is SOUND and my board claim was WRONG.** Our substrate scoring at chance is then a
      GENUINE NEGATIVE about the substrate, and building a new story test would not fix anything --
      we would just have a second test we also fail.
  ONE clearly above chance -> exploitable surface signal exists that our arms never found, which is
      a different and more actionable problem: our representation cannot even reach the shortcuts.
  *Either way this is cheap, needs no substrate read, and settles an open board question with a
  measurement instead of an argument.*

NOTE ON SCOPE: this says what SURFACE methods achieve. It does not establish a ceiling, and it is
not a claim about what the substrate could do with a better read-out.
"""
import collections
import json
import math
import os
import random
import re
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAL = os.path.join(_REPO, "data", "corpora", "social_iqa", "hf_dataset", "validation.jsonl")
TRAIN = os.path.join(_REPO, "data", "corpora", "social_iqa", "hf_dataset", "train.jsonl")

_W = re.compile(r"[a-z']+")
STOP = set("""a an the is are was were be been being do does did to of in on at for with
and or but if then than that this these those it its he she they them his her their you your
i me my we our as by from up out so not no yes will would can could should what how why who
someone something person people others other""".split())


def toks(s):
    return [w for w in _W.findall((s or "").lower()) if w not in STOP and len(w) > 1]


def load(p):
    rows = []
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    val = load(VAL)
    print("validation items: %d" % len(val))
    labels = collections.Counter(r["label"] for r in val)
    n = len(val)
    print("label distribution: %s" % {k: round(v / n, 4) for k, v in sorted(labels.items())})
    maj = max(labels.values()) / n
    print("RANDOM (1/3)           %.4f" % (1.0 / 3.0))
    print("MAJORITY               %.4f   <- the real floor to beat" % maj)

    # corpus frequency from TRAIN answers, so RAREST is not fitted on the thing it scores
    freq = collections.Counter()
    for r in load(TRAIN):
        for k in ("answerA", "answerB", "answerC"):
            freq.update(toks(r[k]))

    def score(pick):
        ok = 0
        for r in val:
            ans = [r["answerA"], r["answerB"], r["answerC"]]
            if str(pick(r, ans) + 1) == str(r["label"]):
                ok += 1
        return ok / len(val)

    rng = random.Random(7)

    def p_random(r, ans):
        return rng.randrange(3)

    def p_longest(r, ans):
        return max(range(3), key=lambda i: len(ans[i]))

    def p_overlap(r, ans):
        cue = set(toks(r["context"]) + toks(r["question"]))
        return max(range(3), key=lambda i: len(cue & set(toks(ans[i]))))

    def p_rarest(r, ans):
        def rarity(i):
            t = toks(ans[i])
            return max((-math.log(freq[w] + 1) for w in t), default=0.0)
        return max(range(3), key=rarity)

    out = {}
    for name, fn in (("RANDOM(sampled)", p_random), ("LONGEST", p_longest),
                     ("OVERLAP", p_overlap), ("RAREST", p_rarest)):
        out[name] = score(fn)
        print("%-22s %.4f" % (name, out[name]))

    print()
    surface = max(out["LONGEST"], out["OVERLAP"], out["RAREST"])
    # A 1,954-item binomial at p=1/3 has sd ~= 0.0107, so ~3sd is about +0.032 over the floor.
    sd = math.sqrt((1 / 3.0) * (2 / 3.0) / len(val))
    bar = maj + 3 * sd
    print("floor = max(majority %.4f) ; 3sd at n=%d is %.4f ; BAR = %.4f"
          % (maj, len(val), 3 * sd, bar))
    print("best surface/artifact method = %.4f" % surface)
    print()
    if surface < bar:
        print("VERDICT: **NO SURFACE OR ARTIFACT METHOD BEATS THE FLOOR.** Answer length, lexical")
        print("overlap and word rarity are all at chance. The dataset carries no shortcut, so a")
        print("crude method scoring at chance is the instrument WORKING, not failing.")
        print("**MY BOARD CLAIM WAS WRONG:** our arms sitting at 0.3501-0.3975 is a GENUINE")
        print("NEGATIVE about the substrate, not an untestable measurement. Building a second")
        print("story test would not fix that -- we would own two tests we fail.")
    else:
        print("VERDICT: **A SURFACE SHORTCUT EXISTS at %.4f and our arms never found it.**" % surface)
        print("That reframes the negative: the problem is not only 'no social reasoning', it is that")
        print("our representation could not reach even the shallow cue. Report both.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
