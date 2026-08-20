"""THE HONEST FLOOR: does the substrate beat a CRUDE COUNT-BASED version of its own idea?

WHY THIS RUN EXISTS -- I FLAGGED MY OWN TEST AS TOO EASY. The sibling run reports the substrate
ranking a known-correct synonym at median 46 / 35 against a FREQUENCY floor at 89 / 60 and UNIFORM
at 197 / 155. Beating UNIFORM is necessary and unimpressive. **Beating FREQUENCY is weaker than it
sounds, because ranking anchors by raw corpus frequency is a strange way to look for a SYNONYM --
synonyms are not especially frequent, so that floor was never really trying.**

THE FLOOR THAT IS ACTUALLY TRYING: **SECOND-ORDER CO-OCCURRENCE.** Synonyms famously do NOT co-occur
(you rarely say "car automobile"), but they occur in SIMILAR CONTEXTS -- that is the distributional
hypothesis, and it is the crude count-based version of precisely what the substrate's accumulated
context vector approximates. **A first-order co-occurrence counter has beaten every arm this project
has fielded all session. Its second-order form is the right opponent here.**

FIVE ARMS, one variable each and every one scored on identical items:
  SUBSTRATE   the substrate's own accumulated vectors, its own cosine, its own signed query
  COOC2       *** THE STRONG FLOOR *** cosine between raw co-occurrence COUNT profiles
  COOC1       first-order: how often do the two words co-occur directly? (expected to be WEAK for
              synonyms -- included precisely so the second-order/first-order distinction is
              measured rather than asserted)
  FREQUENCY   cue-blind, carried over so the two runs can be compared
  UNIFORM     the trivial floor

*** THE READING THAT WOULD DEFLATE TODAY'S POSITIVE RESULT, STATED FIRST SO IT CANNOT BE AVOIDED
LATER: *** if COOC2 matches or beats SUBSTRATE, then "the substrate carries real lexical meaning" is
more honestly "COUNTING carries lexical meaning, and the substrate is a lossy copy of the counter" --
which is the same conclusion four independent routes reached earlier today. That would not erase the
result; it would relocate the credit.

GUARDS:
  * POSITIVE CONTROL on COOC2: a word's own count profile must rank itself first.
  * identical item set across arms -- a word is scored by ALL arms or by none.
  * counts built from the substrate's OWN sentence pool, not a fresh corpus read, so the two sides
    see exactly the same text (a fresh reader is not a matched sample -- that fault cost this
    project a 100% leak once already).
  * n printed per seed.

PRE-COMMITTED READINGS:
  SUBSTRATE beats COOC2, CI-separated -> the substrate encodes something the counts do not. That
      would be the first time all session that our representation beat a counting baseline at
      anything, and it should be VET'd hard before anyone celebrates.
  SUBSTRATE ties COOC2 -> we are a faithful but not superior re-encoding of co-occurrence. Honest,
      unsurprising, and it makes "improve the counts" the lever rather than "improve the code".
  COOC2 beats SUBSTRATE -> we are a LOSSY copy of the counter, on the one task where we looked good.
      Report it as the deflation of today's positive result.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from nltk.corpus import wordnet as wn  # noqa: E402

from hdlab.reading_grounding_loop import content_lemmas  # noqa: E402
from hdlab.substrate import Substrate  # noqa: E402

SEEDS = (7, 101, 20260819)
CORPUS = os.environ.get("DIAG_CORPUS", "simplewiki")
N_READ = int(os.environ.get("DIAG_N_READ", "8000"))
CTX_VOCAB = 3000
ARMS = ("SUBSTRATE", "COOC2", "COOC1", "FREQUENCY", "UNIFORM")


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


def _rank_from_scores(scores, self_i, target_idxs):
    s = scores.copy()
    if self_i is not None:
        s[self_i] = -np.inf
    return min(int(np.sum(s > s[t])) + 1 for t in target_idxs)


rows = []
for seed in SEEDS:
    sub = Substrate(seed=seed)
    total = 0
    while total < N_READ:
        r = sub.read(corpus=CORPUS, n_sentences=min(800, N_READ - total), batch=50,
                     max_patches=1, consolidate_every=200)
        if r.n_sentences == 0:
            break
        total += r.n_sentences

    space = sub.state.space
    anchors, mat = space.anchor_matrix()
    if len(anchors) < 50:
        print("seed %s: only %d anchors -- skipped" % (seed, len(anchors)), flush=True)
        continue
    mat = np.asarray(mat, dtype=np.float64)
    matn = mat / np.maximum(np.linalg.norm(mat, axis=1, keepdims=True), 1e-12)
    pos = {a: i for i, a in enumerate(anchors)}

    # ---- counts from the substrate's OWN pool (matched text, not a fresh read) ----------
    pool = list(sub.state.sentence_pool)
    freq = collections.Counter()
    sents = []
    for s in pool:
        ls = content_lemmas(s)
        sents.append(ls)
        freq.update(ls)
    ctx_vocab = [w for w, _ in freq.most_common(CTX_VOCAB)]
    cidx = {w: i for i, w in enumerate(ctx_vocab)}
    C = np.zeros((len(anchors), len(ctx_vocab)), dtype=np.float64)
    for ls in sents:
        present = [w for w in set(ls) if w in pos]
        if not present:
            continue
        cols = [cidx[w] for w in ls if w in cidx]
        if not cols:
            continue
        for w in present:
            np.add.at(C[pos[w]], cols, 1.0)
    Cn = C / np.maximum(np.linalg.norm(C, axis=1, keepdims=True), 1e-12)

    # POSITIVE CONTROL: a word's own count profile must rank itself first.
    probe = 5 if len(anchors) > 5 else 0
    sim = Cn @ Cn[probe]
    assert int(np.argmax(sim)) == probe, "COOC2 fails self-retrieval -- the count matrix is wrong"
    if seed == SEEDS[0]:
        print("selftest COOC2: a word's own count profile ranks itself first", flush=True)

    forder = np.argsort([-freq.get(a, 0) for a in anchors])
    frank = np.empty(len(anchors), dtype=np.int64)
    frank[forder] = np.arange(len(anchors))

    rng = np.random.default_rng(seed)
    res = {a: [] for a in ARMS}
    sums = getattr(space, "_sums", {})
    for lemma in sorted(sums):
        present = [a for a in synonyms(lemma) if a in pos and a != lemma]
        if not present or lemma not in pos:
            continue
        tgt = [pos[a] for a in present]
        i = pos[lemma]
        q = np.sign(np.asarray(sums[lemma], dtype=np.float64))
        qn = q / max(np.linalg.norm(q), 1e-12)
        res["SUBSTRATE"].append(_rank_from_scores(matn @ qn, i, tgt))
        res["COOC2"].append(_rank_from_scores(Cn @ Cn[i], i, tgt))
        res["COOC1"].append(_rank_from_scores(C[:, cidx[lemma]].copy() if lemma in cidx
                                              else np.zeros(len(anchors)), i, tgt))
        res["FREQUENCY"].append(min(int(frank[t]) + 1 for t in tgt))
        res["UNIFORM"].append(int(rng.integers(1, len(anchors) + 1)))

    if len(res["SUBSTRATE"]) < 30:
        print("seed %s: only %d scorable words -- skipped" % (seed, len(res["SUBSTRATE"])),
              flush=True)
        continue
    rows.append({"seed": seed, "n_anchors": len(anchors), **{a: res[a] for a in ARMS}})
    print("seed %-9s anchors %4d words %4d | " % (seed, len(anchors), len(res["SUBSTRATE"]))
          + "  ".join("%s %6.1f" % (a, np.median(res[a])) for a in ARMS), flush=True)

if len(rows) < 2:
    print("\nfewer than 2 usable seeds -- NO VERDICT")
    raise SystemExit(0)
with open(os.path.join(_REPO, "scratch", "synonym_rank_strong_floor.json"), "w",
          encoding="utf-8") as fh:
    json.dump(rows, fh, indent=1)

rng = np.random.default_rng(0)


def paired(a, b):
    d = np.concatenate([np.asarray(r[a], float) - np.asarray(r[b], float) for r in rows])
    bb = np.array([np.median(d[rng.integers(0, d.size, d.size)]) for _ in range(4000)])
    lo, hi = np.percentile(bb, [2.5, 97.5])
    sep = not (lo <= 0 <= hi)
    print("   %-28s %+8.1f  95%% CI [%+.1f, %+.1f]  %s"
          % ("%s - %s" % (a, b), np.median(d), lo, hi, "SEPARATED" if sep else "not separated"))
    return float(np.median(d)), sep


print("\n" + "=" * 78)
print("POOLED PAIRED (negative = the FIRST arm ranks the correct synonym BETTER):")
d_c2, s_c2 = paired("SUBSTRATE", "COOC2")
paired("SUBSTRATE", "COOC1")
paired("SUBSTRATE", "FREQUENCY")
paired("COOC2", "COOC1")

print()
if s_c2 and d_c2 < 0:
    print("VERDICT: **THE SUBSTRATE BEATS THE COUNT-BASED FLOOR AT ITS OWN GAME.** It encodes")
    print("something second-order co-occurrence does not. That is the first time this session that")
    print("our representation has beaten a counting baseline at anything -- VET IT HARD before")
    print("anyone celebrates: second corpus, and check the floor is not crippled by CTX_VOCAB.")
elif not s_c2:
    print("VERDICT: **WE TIE THE COUNTER.** A faithful but not superior re-encoding of")
    print("co-occurrence. Honest and unsurprising -- and it makes IMPROVING THE COUNTS the lever")
    print("rather than improving the code.")
else:
    print("VERDICT: **THE COUNTER BEATS US ON THE ONE TASK WHERE WE LOOKED GOOD.** Today's")
    print("positive result is deflated: counting carries the lexical meaning and we are a lossy")
    print("copy of it -- the same conclusion four independent routes reached earlier today.")
