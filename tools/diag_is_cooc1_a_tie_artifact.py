"""IS COOC1's WIN A TIE ARTIFACT? The same trap that already killed DG@0.01 today.

WHAT IS BEING CHECKED. The strong-floor run reports first-order co-occurrence ranking a correct
synonym at median **17.0** against the substrate's 46.0 and second-order co-occurrence's 38.0 -- and
I had predicted COOC1 would be WEAK. A result that reverses my prediction and wins by a lot is
exactly when to look for an artifact rather than celebrate.

THE SPECIFIC SUSPICION, stated before the run. `COOC1` scores each anchor by how often it co-occurred
with the target lemma. **For any target that is not common, MOST anchors co-occurred with it ZERO
times.** All those anchors tie at exactly 0.0, and the rank statistic is `1 + #{s > s[target]}` -- a
STRICT inequality -- so when the correct synonym ALSO scores 0, every one of those ties counts as
BEATEN and the synonym gets a flattering rank.

**THIS IS THE THIRD TIME TODAY.** DG@0.01 read 18.0 against a 17.0 floor and turned out to be pure
tie-breaking (random noise scored 14.0). An exactly-100.0% figure turned out to be a wrong field
name. **And CLAUDE.md now carries the rule I wrote this morning -- "report BOTH tie conventions
whenever ties are possible" -- which the strong-floor script does not do.** This closes that gap.

WHAT IT REPORTS, per arm:
  OPTIMISTIC   ties counted as BEATEN     (what the strong-floor run used)
  PESSIMISTIC  ties counted as BEATING
  MIDPOINT     the honest single number when ties are real
  tie density  how many anchors tie with the correct synonym, and on what share of items
  zero share   how much of the score column is exactly 0.0

Deliberately runs at a SMALLER read than the parent: tie STRUCTURE is a structural property of the
score distribution, not a precision measurement, so it does not need the full 8,000 sentences to be
answered -- and the CPU is busy with the runs this is checking.

PRE-COMMITTED READINGS:
  COOC1 keeps its advantage under the PESSIMISTIC convention -> the win is REAL. Direct
      co-occurrence genuinely finds synonyms on encyclopedic text, and the substrate discards that
      signal by design. That is a finding worth acting on.
  COOC1's advantage COLLAPSES under PESSIMISTIC while COOC2's and the SUBSTRATE's do not -> **it was
      tie-breaking**, the strong-floor comparison must be re-scored on the midpoint convention, and
      my prediction that COOC1 would be weak was right for the wrong reason.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from nltk.corpus import wordnet as wn  # noqa: E402

from hdlab.reading_grounding_loop import content_lemmas  # noqa: E402
from hdlab.substrate import Substrate  # noqa: E402

SEED = int(os.environ.get("DIAG_SEED", "7"))
N_READ = int(os.environ.get("DIAG_N_READ", "4000"))
CTX_VOCAB = 3000


def synonyms(w):
    out = set()
    try:
        for s in wn.synsets((w or "").lower()):
            for lem in s.lemma_names():
                out.add(lem.lower().replace("_", " "))
    except Exception:
        pass
    out.discard((w or "").lower())
    return out


def _selftest_conventions():
    t = np.array([0.5, 0.5, 0.5, 0.9])
    opt = 1 + int(np.sum(t > t[0]))
    pes = int(np.sum(t >= t[0]))
    assert opt == 2 and pes == 4, "convention selftest failed: %s %s" % (opt, pes)
    print("selftest conventions: target tied with 2 others below one winner -> "
          "optimistic 2, pessimistic 4", flush=True)


_selftest_conventions()

sub = Substrate(seed=SEED)
total = 0
while total < N_READ:
    r = sub.read(corpus="simplewiki", n_sentences=min(800, N_READ - total), batch=50,
                 max_patches=1, consolidate_every=200)
    if r.n_sentences == 0:
        break
    total += r.n_sentences

space = sub.state.space
anchors, mat = space.anchor_matrix()
mat = np.asarray(mat, dtype=np.float64)
matn = mat / np.maximum(np.linalg.norm(mat, axis=1, keepdims=True), 1e-12)
pos = {a: i for i, a in enumerate(anchors)}

freq = collections.Counter()
sents = []
for s in sub.state.sentence_pool:
    ls = content_lemmas(s)
    sents.append(ls)
    freq.update(ls)
ctx_vocab = [w for w, _ in freq.most_common(CTX_VOCAB)]
cidx = {w: i for i, w in enumerate(ctx_vocab)}
C = np.zeros((len(anchors), len(ctx_vocab)), dtype=np.float64)
for ls in sents:
    cols = [cidx[w] for w in ls if w in cidx]
    if not cols:
        continue
    for w in set(ls):
        if w in pos:
            np.add.at(C[pos[w]], cols, 1.0)
Cn = C / np.maximum(np.linalg.norm(C, axis=1, keepdims=True), 1e-12)

print("\nseed %s | anchors %d" % (SEED, len(anchors)))
print("%-11s %10s %10s %10s | %9s %9s | %8s"
      % ("arm", "OPTIMIS", "MIDPOINT", "PESSIM", "med ties", "%items", "zeros"))
print("-" * 80)

sums = getattr(space, "_sums", {})
items = []
for lemma in sorted(sums):
    present = [a for a in synonyms(lemma) if a in pos and a != lemma]
    if present and lemma in pos:
        items.append((lemma, [pos[a] for a in present]))
print("scorable words: %d" % len(items))


def report(name, score_fn):
    opt, pes, ties, zeros = [], [], [], []
    for lemma, tgt in items:
        s = score_fn(lemma).astype(float).copy()
        s[pos[lemma]] = -np.inf
        best = min(tgt, key=lambda t: -s[t])
        v = s[best]
        gt = int(np.sum(s > v))
        eq = int(np.sum(s == v)) - 1
        opt.append(gt + 1)
        pes.append(gt + eq + 1)
        ties.append(eq)
        zeros.append(float(np.mean(s == 0.0)))
    opt = np.asarray(opt, float)
    pes = np.asarray(pes, float)
    mid = (opt + pes) / 2.0
    print("%-11s %10.1f %10.1f %10.1f | %9.1f %8.1f%% | %7.1f%%"
          % (name, np.median(opt), np.median(mid), np.median(pes), np.median(ties),
             100.0 * np.mean([t > 0 for t in ties]), 100.0 * np.mean(zeros)))
    return np.median(opt), np.median(mid), np.median(pes)


def f_sub(lemma):
    q = np.sign(np.asarray(sums[lemma], dtype=np.float64))
    return matn @ (q / max(np.linalg.norm(q), 1e-12))


s_o, s_m, s_p = report("SUBSTRATE", f_sub)
c2_o, c2_m, c2_p = report("COOC2", lambda lm: Cn @ Cn[pos[lm]])
c1_o, c1_m, c1_p = report("COOC1", lambda lm: C[:, cidx[lm]] if lm in cidx
                          else np.zeros(len(anchors)))

print()
print("COOC1 vs SUBSTRATE under each convention (negative = COOC1 better):")
print("   OPTIMISTIC  %+7.1f" % (c1_o - s_o))
print("   MIDPOINT    %+7.1f" % (c1_m - s_m))
print("   PESSIMISTIC %+7.1f" % (c1_p - s_p))
print()
if c1_p < s_p and c1_o < s_o:
    print("VERDICT: **COOC1's WIN IS REAL -- it survives both tie conventions.** Direct")
    print("co-occurrence genuinely finds synonyms on encyclopedic text ('a car, also called an")
    print("automobile'), and the substrate discards that signal by comparing context PROFILES")
    print("instead. That is a design choice worth revisiting on evidence.")
else:
    print("VERDICT: **TIE-BREAKING ARTIFACT -- WITHDRAW COOC1's WIN.** Optimistic %+.1f becomes"
          % (c1_o - s_o))
    print("%+.1f pessimistic. Most anchors never co-occur with the target, so they tie at exactly"
          % (c1_p - s_p))
    print("0.0 and the strict-inequality rank counts every tie as beaten. THIRD time today.")
    print("The strong-floor comparison must be re-read on the MIDPOINT convention.")
