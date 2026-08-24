"""Vocabulary grows with reading. Whether grounding is CORRECT has never been measured at power.

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

🔴 **AND THEN THE CORRECTION THAT THIS TEST NOW LEADS WITH, BECAUSE I RAN PAST A PRE-REGISTRATION.**
The cell that DEFINES this measurement (`exp_grounding_precision_gold_v1`) carries a pre-committed
reading, written before any number existed:

    "(iv) fewer than ~300 scorable items -> UNDERPOWERED; report the n and the required n,
          and do NOT issue a verdict. A width is not an effect."

**EVERY ARM IS BELOW THAT THRESHOLD. 0 of 12 reach n=300; the maximum n is 151.** So "grounding is
at chance" is NOT an available conclusion -- not mine, and not the submission's "precision sits at
the RANDOM_ANCHOR floor in every arm". **The pre-registration forbids the verdict at this n, and a
pre-registration I did not write is not one I may quietly outgrow.**

**WHAT IS ACTUALLY TRUE, AND IT IS STILL DECISIVE FOR THE DIRECTION:**

  1. **There is NO POWERED MEASUREMENT of whether the substrate's grounding is correct.** Not a
     negative result -- an ABSENT one. We cannot currently tell.
  2. **The reason is itself a finding: a 4,000-sentence read yields only ~151 scorable groundings**,
     so the instrument cannot reach its own power threshold at this reading volume.
  3. **"Read more" STILL does not follow**, but for a sharper reason than I first gave: we would be
     scaling the input of a mechanism whose correctness has never been measured at power.

WHY THE TWO RESULTS ARE NOT IN CONFLICT, WHICH IS THE USEFUL PART. The submission that SUCCEEDED did
not use the substrate's grounding path at all -- it built a PPMI-SVD distributional model over raw
simplewiki text. So:

    the information IS in the text          (distributional statistics extract it, CI-separated)
    whether the substrate extracts it       UNKNOWN -- never measured at power

**SO THE GAP IS NOT READING VOLUME, AND IT IS NOT YET DEMONSTRABLY THE MECHANISM EITHER.** ⚠️ *An
earlier version of this file asserted "the gap IS the extraction mechanism". That inference rested
on the at-chance verdict the pre-registration forbids, so it is withdrawn.* **What the evidence
supports is narrower and more actionable: a plain distributional model over this corpus clears its
floor CI-separated, and we have never been able to say whether ours does.** The next move is a
POWERED grounding measurement, not a scaling run and not a rebuild.

⚠️ **AND A LIMIT ON THE COMPARISON ITSELF, WHICH I CHECKED ON MYSELF:** the distributional result is
Spearman rho on word-pair similarity; the substrate's is anchor-assignment precision against
ConceptNet. **DIFFERENT TASKS, DIFFERENT SCORERS -- the numbers may NOT be compared.** Each is judged
only against ITS OWN floor, which is the only claim made here.

NOT ESTABLISHED, AND STATED SO IT CANNOT TRAVEL FURTHER THAN IT GOES:
  * n=151 scorable with 3 hits is SMALL and BELOW ITS OWN PRE-REGISTERED MINIMUM. It supports
    neither "at chance" nor "working" -- an underpowered test answers nothing in either direction.
  * The precision gold is `conceptnet_gold_v1`. A different gold could score differently, and the
    submission says its coverage is 0.899.
  * Vocabulary growth and grounding precision were measured on DIFFERENT reads. This test asserts
    each against its own source and deliberately computes NO cross-quantity ratio.

    .venv/Scripts/python.exe verification/test_grounding_correctness_has_never_been_measured_at_power.py
"""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESUME = os.path.join(REPO, "data", "exp_substrate_resume_helps_v1", "metrics.json")
# PRE-REGISTERED in exp_grounding_precision_gold_v1 reading (iv), before any number existed.
# This is NOT a threshold I chose and NOT one I may relax -- it is the measuring cell's own band.
PREREG_MIN_N = 300


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
    ns = []
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
            chk("no separation from floor -- but see the power check below (%s)"
                % path.split("/")[-2][:22],
                p > 0.05,
                "p=%.4f, %d hits in %s" % (p, sub.get("hits", -1), sub.get("n", "?")))
            checked += 1
            ns.append(int(sub.get("n") or 0))

    chk("at least one arm was actually tested against its floor", checked > 0,
        "%d arm(s) carried a paired permutation p" % checked)

    # THE LOAD-BEARING CHECK. The defining cell's pre-registration (reading iv) says fewer than
    # ~300 scorable items is UNDERPOWERED and NO VERDICT may be issued. This asserts that we are
    # in that regime, so the file can never quietly drift back into claiming the verdict.
    print("[witness] scorable n per arm: %s | pre-registered requirement: %d"
          % (sorted(ns, reverse=True), PREREG_MIN_N))
    chk("EVERY arm is below the PRE-REGISTERED power threshold -- no verdict is available",
        ns and max(ns) < PREREG_MIN_N,
        "max n = %d < %d, so 'grounding is at chance' is NOT an available conclusion"
        % (max(ns) if ns else 0, PREREG_MIN_N))
    chk("so what we have is an ABSENT measurement, not a negative one",
        True, "%d of %d arms powered" % (sum(1 for n in ns if n >= PREREG_MIN_N), len(ns)))

    print()
    print("[witness] READ AS: vocabulary growth is a STATISTIC and it is climbing; whether the")
    print("[witness] grounding OUTCOME is correct has NEVER been measured at power (max n=151 vs")
    print("[witness] a pre-registered 300). 'Read more' does not follow -- but neither does")
    print("[witness] 'grounding is broken'. The next move is a POWERED measurement.")
    print("[witness] RESULT: %s" % ("ALL WITNESS CHECKS PASS" if ok else "FAILED"))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
