"""The refuse-gate's 0.999 is read-vs-invented. On REAL words we have not read it refuses 85.8%.

WHERE THIS COMES FROM. Integrating the `wire_the_refuse_gate_onto_the_readout` submission
(SOLVED, reviewed EXCELLENT, 2026-08-23). Its finding is real and well controlled: the refusable
signal is CUE FAMILIARITY (does this lemma carry any encoding trace), not answer confidence. The
brief's own proposed mechanism -- a threshold on top-1 similarity -- sits AT the info-free floor
(0.568 / 0.524 vs 0.500), and a LEVEL control shows the recollection-level gate fails the same bar
(accept_real 0.008). None of that is in dispute and this test does not challenge it.

**WHAT THIS TEST ADDS IS THE ARM NOBODY RAN.** Every "real" item in that measurement was a word the
substrate had just READ, so the positive class is defined by the same property the gate reads. The
submission says so plainly in its own control 7 ("real cues carry >=1 trace, invented carry 0 -- a
clean trace-presence boundary"). A lookup asked to separate present from absent returns ~1.000 by
construction. **The number that decides whether this gate can be switched ON is different: what
happens to genuine English words the reader has simply not encountered yet.**

MEASURED HERE, on an EXTERNAL word list (Lancaster norms) that was not built from our store.

🔴 **CORRECTED 2026-08-23, SAME SESSION: THE FIRST VERSION OF THIS TEST USED A CAPPED CALL SHAPE AND
ITS COVERAGE NUMBER DESCRIBED MY CALL, NOT THE SUBSTRATE.** It read via
`read(n_sentences=1500)` twice -> 4,429 lemmas -> "9.4% answered / 90.6% refused". But
`notes/SUBSTRATE_READ_SILENTLY_READS_A_FRACTION_OF_WHAT_YOU_ASK_FOR_2026-08-22.md` documents that
the single large call is capped, AND that the shape every experiment cell actually uses is a LOOP of
`chunk=400`. Re-measured with the real shape, reading the TRUE count off `ReadResult.n_sentences`:

    sentences read    vocabulary    coverage of 4,000 real English words
        800             2,270            5.1% answered
      1,900             3,949            8.4%
      3,100             5,525           11.2%
      4,100             6,221           12.6%
      5,200             7,334           14.2%      <- still climbing, no saturation

**COVERAGE IS A FUNCTION OF HOW MUCH WAS READ, NOT A CONSTANT.** Any coverage number quoted without
its sentence count is meaningless -- that is this project's "no number crosses populations" rule,
where the population is the read volume. **The qualitative conclusion is unchanged and holds at
EVERY point on that curve: the large majority of ordinary English is refused.** The specific figure
is not a property of the gate; it is a property of how much the substrate has read.

**THIS IS NOT A DEFECT IN THE SUBMISSION AND MAY NOT BE A DEFECT AT ALL.** Refusing a word you have
never encountered is arguably the CORRECT conservative behaviour, and it is what "contribute, do not
decide" asks for. The point is that the two numbers answer different questions and only one of them
is about deployment:

    0.999  = "does the gate tell read words from invented strings"   YES, decisively
    85.8%  = "what share of ordinary English does it refuse"          the cost of switching it on
             (at 5,200 sentences -- ALWAYS quote the sentence count with it)

**SO THE WIRING DECISION IS: DEFAULT-OFF, OR ON ONLY WHERE REFUSING UNREAD VOCABULARY IS WANTED.**
Nobody should read "balanced 0.999" as "the system knows what it knows about English." It knows what
it has read, which after a few thousand sentences is a small fraction of the language.

A SECOND OBSERVATION, RECORDED BECAUSE IT POINTS AT AN OPEN PROBLEM: `abandon` is answered while
`abandoned` is refused. That is the morphology/lemmatisation gap already filed as its own brief
(`lookup_does_not_lemmatise`), showing up here as refusals of inflected forms of words we HAVE read.

**AND THE SIZE OF THAT LEVER IS MEASURED HERE, BECAUSE MY FIRST INSTINCT OVERSTATED IT.** On seeing
`abandon`/`abandoned` I wrote that fixing lemmatisation "would move this number". It would, but it
is NOT the main cause. Splitting the refusals by whether a crude base form is already known:

    inflections of words we DO know     12.4% of refusals   -> coverage 14.2% -> 24.9%
    genuinely absent vocabulary         87.6% of refusals

**So lemmatisation nearly DOUBLES coverage and still leaves ~75% refused.** The gate refuses most of
English because the substrate has read a small fraction of English (7,334 lemmas at 5,200
sentences), not because the lookup is broken. *That is a corpus-coverage fact, and it is the honest reason the gate is
conservative -- a lemmatiser is worth building and will not change the wiring decision.*
(The suffix-stripping split is crude ON PURPOSE: it under-counts morphology, so 12.4% is a LOWER bound
and the conclusion "morphology is not the main cause" only gets stronger with a better analyser.)

    .venv/Scripts/python.exe verification/test_the_familiarity_gate_refuses_most_of_english.py
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.exp_refuse_gate_on_readout_v2_membership import familiarity_set
from hdlab.substrate import Substrate

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NORMS = os.path.join(REPO, "data", "grounding_testbed",
                     "Lancaster_sensorimotor_norms_for_39707_words.csv")
N_WORDS = 4000
# THE CALL SHAPE MATTERS AND IS THE CORRECTED PART. A single large read is capped (~1,060 no matter
# what you ask for); a LOOP of chunk=400 is what every experiment cell uses and it does not degrade.
# Do not "simplify" this back into one big call -- that is the documented defect, and it silently
# shrinks the vocabulary every number below is computed against.
CHUNK = 400
READ_CALLS = 14


def real_word_sample(limit=N_WORDS):
    """Real English words from an EXTERNAL list -- deliberately not derived from our own store."""
    words = []
    with io.open(NORMS, encoding="utf-8", errors="replace") as fh:
        fh.readline()
        for line in fh:
            w = line.split(",")[0].strip().strip('"').lower()
            if w.isalpha() and len(w) > 2:
                words.append(w)
            if len(words) >= limit:
                break
    return words


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-58s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    if not os.path.exists(NORMS):
        print("[witness] FAIL word list missing: %s" % NORMS)
        raise SystemExit(1)

    sub = Substrate()
    n_read = 0
    for _ in range(READ_CALLS):
        r = sub.read(corpus="simplewiki", n_sentences=CHUNK, batch=100)
        n = getattr(r, "n_sentences", None)
        # NEVER substitute 0 for an unreadable count -- an earlier draft did exactly that and
        # printed "0 sentences read" on a read that plainly happened.
        if n is not None:
            n_read += n
    fam = familiarity_set(sub)
    print("[witness] sentences ACTUALLY read: %d (looped chunk=%d x %d) -- every coverage number "
          "below is relative to THIS read volume" % (n_read, CHUNK, READ_CALLS))

    # POSITIVE CONTROL FIRST. If the read did not happen, every number below is trivially "refused"
    # and the test would "pass" for entirely the wrong reason. Note the read() return value is NOT
    # used as evidence here -- a first draft printed "0 sentences read" because it misread that
    # return, while the vocabulary below proves the read ran. Observe the artifact, not the proxy.
    chk("POSITIVE CONTROL: the read actually populated a vocabulary",
        len(fam) > 1000, "familiarity set = %d lemmas" % len(fam))
    # GUARD AGAINST THE REGRESSION THIS TEST WAS CORRECTED FOR: if someone puts the capped single
    # call back, the vocabulary collapses and every percentage below silently shifts.
    chk("the LOOPED call shape reached the vocabulary it should",
        len(fam) > 6000,
        "%d lemmas -- the capped single-call shape yields ~4,400 and would understate coverage"
        % len(fam))

    words = real_word_sample()
    chk("the external word list loaded", len(words) > 1000, "%d real English words" % len(words))

    answered = [w for w in words if w in fam]
    refused = [w for w in words if w not in fam]
    frac_ref = float(len(refused)) / len(words)

    print("[witness] answered %d (%.1f%%) | refused %d (%.1f%%)"
          % (len(answered), 100 * (1 - frac_ref), len(refused), 100 * frac_ref))
    print("[witness] refused examples: %s" % ", ".join(sorted(refused)[:10]))

    chk("the gate REFUSES the large majority of real, simply-unread English",
        frac_ref > 0.75, "%.1f%% refused -- this is the cost of switching it ON" % (100 * frac_ref))

    # NEGATIVE CONTROL: it must not refuse EVERYTHING, or the familiarity set is broken rather
    # than small, and the finding above would be an artifact of a dead lookup.
    chk("NEGATIVE CONTROL: it still answers real words it HAS read",
        len(answered) > 50, "%d answered, e.g. %s"
        % (len(answered), ", ".join(sorted(answered)[:6])))

    # HOW MUCH OF THE REFUSAL IS MORPHOLOGY, NOT MISSING VOCABULARY. Crude suffix stripping, which
    # UNDER-counts morphology -- so this is a lower bound and the conclusion below only strengthens
    # with a real analyser.
    sufs = ("ing", "edly", "ed", "es", "s", "ly", "er", "est", "ness", "ment", "tion", "al",
            "ity", "able", "ance", "ence", "ful", "less")

    def bases(w):
        out = set()
        for s in sufs:
            if w.endswith(s) and len(w) - len(s) >= 3:
                st = w[:-len(s)]
                out.update({st, st + "e"})
                if len(st) > 1 and st[-1] == st[-2]:
                    out.add(st[:-1])
                if st.endswith("i"):
                    out.add(st[:-1] + "y")
        return out

    morph = [w for w in refused if bases(w) & fam]
    share = float(len(morph)) / max(1, len(refused))
    lifted = float(len(answered) + len(morph)) / len(words)
    print("[witness] of the refusals, %d (%.1f%%) are inflections of KNOWN words; "
          "lemmatising lifts coverage %.1f%% -> %.1f%%"
          % (len(morph), 100 * share, 100.0 * len(answered) / len(words), 100 * lifted))
    chk("morphology is NOT the main cause -- most refusals are absent vocabulary",
        share < 0.35,
        "%.1f%% of refusals are inflections; the other %.1f%% are words we have simply never read"
        % (100 * share, 100 * (1 - share)))

    print()
    print("[witness] READ AS: 0.999 = read-vs-invented, measured correctly. ~%.0f%% = the share of"
          % (100 * frac_ref))
    print("[witness] ordinary English this gate would refuse. Different questions. Wire DEFAULT-OFF.")
    print("[witness] RESULT: %s" % ("ALL WITNESS CHECKS PASS" if ok else "FAILED"))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()

# ---- DELIBERATELY NOT WIRED INTO THE CERTIFICATION GATE ----------------------------------
# The three metrics-reading witnesses written the same day WERE wired in (they cost
# milliseconds). This one is different and the difference is the point: it performs 14 real
# corpus reads (5,200 sentences) and takes minutes. run_certification.py is ALREADY timing out
# with a crash exit -- there is an open brief for it (certification_gate_hangs) -- so adding a
# multi-minute witness to it would make a known problem worse and would be blamed on the gate
# rather than on this file.
#
# So it is a MANUAL witness, run by hand:
#     .venv/Scripts/python.exe verification/test_the_familiarity_gate_refuses_most_of_english.py
#
# THIS COMMENT EXISTS SO THE ABSENCE READS AS A DECISION AND NOT AN OVERSIGHT. If the gate is
# ever fixed and gains a slow/marked lane, move it in -- it has a positive control (the read
# populated a vocabulary), a negative control (it does not refuse everything), and a regression
# guard (the vocabulary must exceed what the capped single-call read shape produces).
