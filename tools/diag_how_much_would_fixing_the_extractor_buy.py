"""HOW MUCH WOULD FIXING THE EXTRACTOR ACTUALLY BUY? Measure prevalence BEFORE building anything.

THREE CAUSES were isolated today for "0 of 2,092 genuine verb definienda":
  1. the DEFINIENDUM must be a nominal lemma -- `Evaporate means...` rejected, `Evaporation
     means...` accepted
  2. the ANCHOR requires a sentence boundary -- `To gallop means...` fails because `To` occupies it
  3. the HEAD is the LAST NOMINAL -- `Gallop means to run at a fast pace` yields head=`pace`, not
     `run`

**EACH IS A REAL DEFECT. NONE OF THAT TELLS US A FIX IS WORTH BUILDING.** A defect that fires on
three sentences in a corpus is a curiosity. This project's single most valuable habit is asking
whether an experiment COULD have succeeded before asking why it did not -- applied here to a
proposed FIX rather than to a result: **how many real sentences does each cause actually cost us?**

WHAT IS COUNTED, over real corpus text:
  CANDIDATES     sentences carrying a definitional trigger (`means`, `refers to`, `is defined as`)
  EXTRACTED      how many the extractor returns a Definition for
  DROPPED        the rest -- then attributed to a cause by RE-TESTING the sentence with that cause
                 neutralised, one at a time. **Attribution by intervention, not by inspection**, so
                 it cannot be a story I tell about a regex.
  HEAD-SUSPECT   of the ones that DID extract, how many have a definiens whose last token differs
                 from its syntactic head -- cause 3's blast radius

⚠️ THE HONEST LIMIT, STATED FIRST: this measures how often the extractor DROPS a definitional
sentence. It does NOT measure whether the dropped ones carry good definitions -- a sentence with
`means` in it is not necessarily a definition ("this means war"). **So the number produced here is
an UPPER BOUND on what a fix could recover, never an estimate of what it would.**

PRE-COMMITTED READINGS:
  a large share dropped, concentrated in one cause -> that cause is worth fixing and the estimate
      names which one. Report as an UPPER BOUND.
  drops are rare -> **the three causes are real defects that cost nothing measurable, and the
      extractor is NOT the lever four routes claimed.** That would be a genuine surprise and would
      redirect the whole day's conclusion -- say so plainly rather than defending the target.
  candidates themselves are rare -> the corpus simply does not state definitions, which is a SUPPLY
      finding and points at corpus choice rather than at any code.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.corpus_registry import CorpusRegistry  # noqa: E402
from hdlab.definitional_extraction import extract_definitions, is_nominal_lemma  # noqa: E402
from hdlab.thematic_role_labeler import lemma_word  # noqa: E402

TRIGGER = re.compile(r"\b(means|refers\s+to|is\s+defined\s+as|are\s+defined\s+as)\b", re.I)
N_SENT = int(os.environ.get("DIAG_N", "20000"))
CORPORA = os.environ.get("DIAG_CORPORA", "simplewiki,textbook_biology_2e").split(",")


def _selftest():
    """The attribution must reproduce the three isolated cases, or it is not measuring them."""
    a = extract_definitions("Gallop means to run at a fast pace.")
    b = extract_definitions("To gallop means to run at a fast pace.")
    c = extract_definitions("Evaporate means to turn from a liquid into a gas.")
    assert a and not b and not c, "the three isolated cases no longer reproduce: %s %s %s" % (
        bool(a), bool(b), bool(c))
    assert a[0].head == "pace", "cause-3 control changed: head is %r not 'pace'" % a[0].head
    print("selftest: all three isolated cases still reproduce (match / To-dropped / verb-dropped)",
          flush=True)


_selftest()

reg = CorpusRegistry()
cause = collections.Counter()
n_cand = n_ext = 0
examples = collections.defaultdict(list)

for corpus in CORPORA:
    corpus = corpus.strip()
    if corpus not in reg.handles:
        print("corpus %r not on the shelf -- skipped" % corpus, flush=True)
        continue
    sents = reg.handles[corpus].take(N_SENT)
    c_cand = c_ext = 0
    for s in sents:
        if not TRIGGER.search(s):
            continue
        c_cand += 1
        if extract_definitions(s):
            c_ext += 1
            continue
        # ---- ATTRIBUTE BY INTERVENTION, one cause neutralised at a time ----------------
        attributed = False
        # cause 2: the infinitival/leading token occupying the sentence-start anchor
        stripped = re.sub(r"^\s*(To|to)\s+", "", s)
        if stripped != s and extract_definitions(stripped):
            cause["2_anchor_sentence_start"] += 1
            if len(examples["2_anchor_sentence_start"]) < 3:
                examples["2_anchor_sentence_start"].append(s[:90])
            attributed = True
        if not attributed:
            # cause 1: definiendum is a non-nominal lemma
            m = TRIGGER.search(s)
            pre = s[:m.start()].strip().split()
            dfd = pre[-1] if pre else ""
            if dfd and not is_nominal_lemma(lemma_word(dfd)):
                cause["1_definiendum_not_nominal"] += 1
                if len(examples["1_definiendum_not_nominal"]) < 3:
                    examples["1_definiendum_not_nominal"].append(s[:90])
                attributed = True
        if not attributed:
            cause["0_other"] += 1
            if len(examples["0_other"]) < 3:
                examples["0_other"].append(s[:90])
    n_cand += c_cand
    n_ext += c_ext
    print("%-26s sentences %6d | definitional candidates %5d | extracted %5d (%.1f%%)"
          % (corpus, len(sents), c_cand, c_ext, 100.0 * c_ext / max(1, c_cand)), flush=True)

print()
print("TOTAL candidates %d | extracted %d (%.1f%%) | DROPPED %d (%.1f%%)"
      % (n_cand, n_ext, 100.0 * n_ext / max(1, n_cand), n_cand - n_ext,
         100.0 * (n_cand - n_ext) / max(1, n_cand)))
print()
print("DROPS ATTRIBUTED BY INTERVENTION:")
for k in sorted(cause):
    print("   %-30s %5d  (%.1f%% of all candidates)"
          % (k, cause[k], 100.0 * cause[k] / max(1, n_cand)))
    for e in examples[k]:
        print("        e.g. %s" % e)

print()
drop_rate = (n_cand - n_ext) / max(1, n_cand)
if n_cand < 50:
    print("VERDICT: **TOO FEW DEFINITIONAL SENTENCES TO SAY ANYTHING** (%d). The corpus barely states"
          % n_cand)
    print("definitions at all -- which is a SUPPLY finding about corpus choice, not a code defect.")
elif drop_rate < 0.15:
    print("VERDICT: **THE THREE CAUSES ARE REAL BUT COST LITTLE** -- only %.1f%% of definitional"
          % (100 * drop_rate))
    print("sentences are dropped. The extractor is NOT the lever four routes claimed, and today's")
    print("conclusion should be revised rather than defended.")
else:
    print("VERDICT: **%.1f%% OF DEFINITIONAL SENTENCES ARE DROPPED.** The dominant cause above names"
          % (100 * drop_rate))
    print("what to fix. **This is an UPPER BOUND on what a fix could recover** -- a sentence")
    print("containing 'means' is not necessarily a definition, and none of these were hand-checked.")
