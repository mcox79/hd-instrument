"""The refuse-gate's 0.999 is read-vs-invented. On REAL words we have not read, it refuses ~90%.

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

MEASURED HERE, on an EXTERNAL word list (Lancaster norms) that was not built from our store:

    familiarity set after the read      ~4,400 lemmas
    real English words sampled           4,000
    would be ANSWERED                    ~9%
    would be REFUSED                    ~91%      <- abdomen, abduct, aardvark, abandoned

**THIS IS NOT A DEFECT IN THE SUBMISSION AND MAY NOT BE A DEFECT AT ALL.** Refusing a word you have
never encountered is arguably the CORRECT conservative behaviour, and it is what "contribute, do not
decide" asks for. The point is that the two numbers answer different questions and only one of them
is about deployment:

    0.999  = "does the gate tell read words from invented strings"   YES, decisively
    ~91%   = "what fraction of ordinary English does it refuse"       the cost of switching it on

**SO THE WIRING DECISION IS: DEFAULT-OFF, OR ON ONLY WHERE REFUSING UNREAD VOCABULARY IS WANTED.**
Nobody should read "balanced 0.999" as "the system knows what it knows about English." It knows what
it has read, which after a few thousand sentences is a small fraction of the language.

A SECOND OBSERVATION, RECORDED BECAUSE IT POINTS AT AN OPEN PROBLEM: `abandon` is answered while
`abandoned` is refused. That is the morphology/lemmatisation gap already filed as its own brief
(`lookup_does_not_lemmatise`), showing up here as refusals of inflected forms of words we HAVE read.

**AND THE SIZE OF THAT LEVER IS MEASURED HERE, BECAUSE MY FIRST INSTINCT OVERSTATED IT.** On seeing
`abandon`/`abandoned` I wrote that fixing lemmatisation "would move this number". It would, but it
is NOT the main cause. Splitting the refusals by whether a crude base form is already known:

    inflections of words we DO know     ~9% of refusals   -> coverage 9.4% -> 17.5%
    genuinely absent vocabulary        ~91% of refusals

**So lemmatisation nearly DOUBLES coverage and still leaves ~82% refused.** The gate refuses most of
English because the substrate has read a small fraction of English (~4,400 lemmas), not because the
lookup is broken. *That is a corpus-coverage fact, and it is the honest reason the gate is
conservative -- a lemmatiser is worth building and will not change the wiring decision.*
(The suffix-stripping split is crude ON PURPOSE: it under-counts morphology, so ~9% is a LOWER bound
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
N_SENT = 1500
READ_CALLS = 2


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
    for _ in range(READ_CALLS):
        sub.read(corpus="simplewiki", n_sentences=N_SENT, batch=100)
    fam = familiarity_set(sub)

    # POSITIVE CONTROL FIRST. If the read did not happen, every number below is trivially "refused"
    # and the test would "pass" for entirely the wrong reason. Note the read() return value is NOT
    # used as evidence here -- a first draft printed "0 sentences read" because it misread that
    # return, while the vocabulary below proves the read ran. Observe the artifact, not the proxy.
    chk("POSITIVE CONTROL: the read actually populated a vocabulary",
        len(fam) > 1000, "familiarity set = %d lemmas" % len(fam))

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
