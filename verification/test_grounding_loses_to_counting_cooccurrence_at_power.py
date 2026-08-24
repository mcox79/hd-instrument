"""At power, the substrate's grounding beats random but LOSES 2-3x to counting co-occurrence.

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

🔴🔴 **AND THEN A SECOND CORRECTION, WHICH RETIRES THE FIRST: A POWERED MEASUREMENT ALREADY EXISTS
AND I HAD NOT LOOKED AT IT.** I wrote "there is NO powered measurement of whether grounding is
correct". **That was wrong.** `data/exp_grounding_precision_gold_v1/metrics.json` -- the SAME cell
whose pre-registration I had just quoted -- ran three seeds at `n_read ~40,000` and reports
`UNDERPOWERED: False`, `min_scorable_required: 300`, `n_scorable` = **441 / 441 / 398**.

*I quoted that cell's power rule while never opening its results. The underpowered arm was the
RESUME cell (a 4,000-sentence read); the DEFINING cell had the answer at power all along.* **Same
fault as every other one tonight: I read one archive and not the neighbouring one.**

**THE POWERED ANSWER, ALL THREE SEEDS:**

    seed        n     SUBSTRATE                RANDOM_ANCHOR        TOP_COOCCURRENT
    101        441    0.0272 [.0136,.0431]     0.0045   p=0.0110    0.0590 [.0385,.0816]
    20260819   441    0.0159 [.0045,.0272]     0.0023   p=0.0695    0.0476 [.0295,.0680]
    7          398    0.0302 [.0151,.0477]     0.0025   p=0.0050    0.0653 [.0427,.0905]

  1. **The substrate BEATS the random floor on 2 of 3 seeds** (p=0.011, p=0.005; the third at
     p=0.069). **So grounding is NOT noise** -- and my "at chance" was wrong in that direction too.
  2. 🔻 **BUT A TRIVIAL "MOST CO-OCCURRING WORD" BASELINE SCORES 2-3x HIGHER ON EVERY SEED.** The
     cell PRE-COMMITTED this reading: *"(iii) SUBSTRATE beats RANDOM but ties TOP_COOCCURRENT -> what
     it has learned is co-occurrence, which is this project's standing diagnosis arriving on a third
     instrument."* **The observed case is worse than the tie it anticipated.**
  3. **Absolute precision is ~1.6-3.0% either way.** Whatever is being assigned, it is rarely the
     gold neighbour.
  4. **"Read more" still does not follow** -- these are ~40,000-sentence reads, ten times the volume
     of the underpowered arm, and the ordering does not improve.

WHY THE TWO RESULTS ARE NOT IN CONFLICT, WHICH IS THE USEFUL PART. The submission that SUCCEEDED did
not use the substrate's grounding path at all -- it built a PPMI-SVD distributional model over raw
simplewiki text. So:

    the information IS in the text          (distributional statistics extract it, CI-separated)
    the substrate extracts SOME of it       beats random on 2/3 seeds, at power
    but counting co-occurrence does better  2-3x, on 3 of 3 seeds

**SO THE GAP IS NOT READING VOLUME.** These are ~40,000-sentence reads -- ten times the underpowered
arm -- and the ordering does not improve. ⚠️ *An earlier version of this file asserted "the gap IS
the extraction mechanism" while resting on a forbidden verdict; that phrasing is withdrawn, but the
powered data now supports a precise version of it:* **the mechanism is beaten, on its own task and
its own gold, by the simplest possible summary of the same text.** *A mechanism that does not beat
the baseline it is meant to explain is not yet doing the thing it is for.*

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

    .venv/Scripts/python.exe verification/test_grounding_loses_to_counting_cooccurrence_at_power.py
"""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESUME = os.path.join(REPO, "data", "exp_substrate_resume_helps_v1", "metrics.json")
# PRE-REGISTERED in exp_grounding_precision_gold_v1 reading (iv), before any number existed.
# This is NOT a threshold I chose and NOT one I may relax -- it is the measuring cell's own band.
PREREG_MIN_N = 300
POWERED = os.path.join(REPO, "data", "exp_grounding_precision_gold_v1", "metrics.json")


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
    chk("that RESUME arm is underpowered", True,
        "%d of %d arms powered" % (sum(1 for n in ns if n >= PREREG_MIN_N), len(ns)))

    # ---- THE POWERED CELL, WHICH I INITIALLY FAILED TO OPEN -------------------------------
    # Same cell whose pre-registration is quoted above. It ran ~40,000-sentence reads and IS
    # powered. Quoting a cell's rules while never reading its results is how the first version
    # of this file came to claim no powered measurement existed.
    if not os.path.exists(POWERED):
        print("[witness] FAIL missing the powered cell: %s" % POWERED)
        raise SystemExit(1)
    with io.open(POWERED, encoding="utf-8") as fh:
        pm = json.load(fh)

    beats_random, loses_to_cooc, powered_units = 0, 0, 0
    print()
    for uk, u in sorted(pm["units"].items()):
        sub, rnd = u.get("SUBSTRATE", {}), u.get("RANDOM_ANCHOR", {})
        cooc = u.get("TOP_COOCCURRENT", {})
        if sub.get("precision") is None:
            continue
        powered_units += 1
        p = rnd.get("paired_perm_p_vs_SUBSTRATE")
        print("[witness]   seed %-10s n=%-5s UNDERPOWERED=%-6s SUBSTRATE %.4f  RANDOM %.4f (p=%s)"
              "  TOP_COOCCURRENT %.4f"
              % (uk.split("|")[-1], u.get("n_scorable"), u.get("UNDERPOWERED"),
                 sub["precision"], rnd.get("precision", float("nan")), p,
                 cooc.get("precision", float("nan"))))
        chk("  this arm IS powered by its own rule (seed %s)" % uk.split("|")[-1],
            u.get("UNDERPOWERED") is False and (u.get("n_scorable") or 0) >= PREREG_MIN_N,
            "n_scorable=%s required=%s" % (u.get("n_scorable"), u.get("min_scorable_required")))
        if p is not None and p < 0.05:
            beats_random += 1
        if cooc.get("precision") is not None and cooc["precision"] > sub["precision"]:
            loses_to_cooc += 1

    chk("grounding is NOT noise -- it beats the random floor on most seeds",
        beats_random >= 2, "%d of %d seeds separated from RANDOM_ANCHOR"
        % (beats_random, powered_units))
    chk("but a TRIVIAL co-occurrence count beats it on EVERY seed",
        loses_to_cooc == powered_units,
        "%d of %d seeds: TOP_COOCCURRENT > SUBSTRATE" % (loses_to_cooc, powered_units))

    print()
    print("[witness] READ AS: at power, grounding beats random but LOSES 2-3x to counting")
    print("[witness] co-occurrence, on every seed, at ~40,000-sentence reads. 'Read more' does")
    print("[witness] not follow. The mechanism does not beat the baseline it is supposed to explain.")
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
def test_grounding_loses_to_counting_at_power():
    try:
        main()
    except SystemExit as exc:
        assert exc.code == 0, "witness FAILED (exit %r) -- run the file directly for the detail" % (exc.code,)
