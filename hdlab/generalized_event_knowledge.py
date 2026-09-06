"""hdlab/generalized_event_knowledge.py -- the FORWARD generalized-event-knowledge (GEK) organ:
the missing FORWARD half of the discourse/event predictive hierarchy (owner-DONE
predictive_inference_forward_project_the_next_event_and_state_from_the_situation_model, Q111 landing).

WHAT THIS ORGAN COMPUTES (the brain operation, PINNED).
Forward prediction during comprehension is a GRADED ASSOCIATIVE CO-ACTIVATION READOUT over GENERALIZED
EVENT KNOWLEDGE (Elman 2009 "On the meaning of words and dinosaur bones"; Metusalem 2012; Hare 2009;
McRae & Matsuki) -- the brain reads out how expected an upcoming event's content is given the situation
so far. It is NOT a discrete script lookup; it is a graded associative readout of what-content-follows-
what, learned self-supervised from a narrative corpus's own story transitions. Precision = distribution
concentration / inverse entropy (Kuperberg & Jaeger 2016; Hale entropy-reduction). The substrate builds a
rich BACKWARD situation model (situation_reader) and an argument-level forward surprisal
(predict_surprisal) and a BACKWARD event monitor (n400_coherence_monitor), but had NO forward EVENT-level
projector -- the generator the N400/EST error is meant to be taken against. This organ is that generator.

THE OPERATION (glass-box, NO LLM, deterministic).
  * STORE: a directed forward-transition association -- PPMI over "what content follows what" across the
    sentences of a story, learned OFFLINE from ROCStories-train (a STATIC ADMISSIBLE FOUNDATION ASSET;
    the invariant is NO external LLM at inference, not no offline asset). Frozen to a compact CSR npz.
  * READOUT (discrimination -- the validated headline): score each candidate continuation by how expected
    its content is given the context content (the GEK content cue) and given the agent's open goal text
    (the goal cue), COMPOSE the two cues via hdlab.graded_competition (additive Lewis-Vasishth activation
    -> softmax posterior), pick the argmax, precision = 1 - normalized entropy of the maintained 2-way
    distribution. This is the byte-faithful spine of experiments/exp_forward_event_projection_v1.py (the
    directed-forward MECHANISM `make_scorer(S,"fwd")`) + the graded_competition multi-cue combination of
    experiments/exp_forward_event_projection_situation_model_v1.py (GEK content + goal, equal weights on
    standardized cues).
  * READOUT (generative -- expected content, not a validated capability claim): the top-k forward-expected
    content tokens = argmax_w sum_a PPMI(a, w) over the context content a. Provided for on-demand
    elaboration; the SOLVED did NOT establish a generative next-predicate result (it validated the
    right-vs-wrong CONTINUATION discrimination), so this is offered glass-box, uncalibrated.

VALIDATED (the discrimination readout, full Story Cloze val 1871 + test 1871; store = ROCStories-train
98,161 stories, DISJOINT from the eval): forward GEK projection val 0.5922 [0.570,0.615] / test 0.5815
[0.559,0.604], CI-SEPARATED over the majority-continuation floor (val +0.078 / test +0.068); the
cross-context info-free twin COLLAPSES to chance (0.491 / 0.489); a calibrated precision (1 - normalized
entropy) earns MONOTONICALLY RISING selective accuracy (val 0.592->0.654). LOCATED NEGATIVE (a full PASS
per the bar): the projection ties -- does NOT robustly exceed -- a 1-step co-occurrence counter (val +0.010,
CI incl 0). Do NOT wire the successor/horizon (adds nothing) or a finer verb-structure grain (weaker) --
compose the CONTENT GEK cue + goal cue only.

DEFAULT-SAFE / ISLAND: a NEW module -- importing it changes NO existing behaviour. The frozen store is a
large gitignored data asset (the whole data/ tree is gitignored); the organ DEGRADES GRACEFULLY
(available()==False -> score/project return None/0 / abstain, never raise) when it is absent, so a
default-on live consumer is safe in an asset-less environment. The offline build (python -m
hdlab.generalized_event_knowledge --build) fits the store from data/corpora/roc_stories/train.jsonl in
~15s and freezes it -- a static offline asset, run once. Glass-box. NO external LLM at inference. ASCII.
"""
from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEK_ASSET = os.path.join(_REPO, "data", "frontend_assets", "generalized_event_knowledge_roc_fwd.npz")
ROC_JSONL = os.path.join(_REPO, "data", "corpora", "roc_stories", "train.jsonl")

VOCAB_CAP = 8000
_EPS = 1e-12

# byte-faithful to experiments/exp_forward_event_projection_v1.py (the store the validated result used)
STOP = set("a an the of to and or but if then so as at by for from in into on onto with without over under "
           "is are was were be been being am do does did done has have had having will would shall should can "
           "could may might must not no nor this that these those it its he she they them him her his their our "
           "we you i me my your out up down off about again very just too also there here what which who whom "
           "when where why how all any both each few more most other some such only own same than s t re ve ll d "
           "m o one two now day time back said say says her him his them".split())


# --------------------------------------------------------------------------- lemmatizer (byte-faithful)
_LEM_CACHE: Dict[str, str] = {}
_WN = None
_WN_MISSING = False


def _wordnet():
    """The WordNet corpus reader, loaded ONCE (lazy). None if unavailable -- lemmatize degrades to identity."""
    global _WN, _WN_MISSING
    if _WN is None and not _WN_MISSING:
        try:
            from nltk.corpus import wordnet as wn
            wn.morphy("test")  # force the lazy corpus load now so later calls cannot raise
            _WN = wn
        except Exception:
            _WN_MISSING = True
            _WN = None
    return _WN


def lemmatize(text: str) -> List[str]:
    """Content-lemma bag of `text`, byte-faithful to exp_forward_event_projection_v1._lemmas_factory:
    lowercase, [a-zA-Z]+ tokens, drop len<3 and STOP words, WordNet morphy (NOUN then VERB) else the token.
    Lazy -- loads WordNet only on first call (the default reader that never invokes prediction pays nothing).
    Degrades to the raw token (no morphy) if WordNet is absent -- the store keys are morphy lemmas, so an
    absent WordNet simply lowers coverage, never raises."""
    if not text:
        return []
    wn = _wordnet()
    out: List[str] = []
    for tok in re.findall(r"[a-zA-Z]+", text.lower()):
        if len(tok) < 3 or tok in STOP:
            continue
        lem = _LEM_CACHE.get(tok)
        if lem is None:
            if wn is not None:
                lem = wn.morphy(tok, wn.NOUN) or wn.morphy(tok, wn.VERB) or tok
            else:
                lem = tok
            _LEM_CACHE[tok] = lem
        out.append(lem)
    return out


# --------------------------------------------------------------------------- frozen store (lazy singleton)
_STORE: Optional[Dict] = None
_STORE_MISSING = False


def _store() -> Optional[Dict]:
    """The frozen forward-transition GEK store as a CSR view, loaded ONCE. None (not an exception) if the
    gitignored asset is absent -- callers degrade to abstain. Keys:
      vocab (list[str]), wid (word->id), indptr (int64[V+1]), indices (int32[nnz] target ids sorted per row),
      data (int32[nnz] joint counts), src (int64[V] row-sum marginals), tgt (int64[V] col-sum marginals),
      tf (float total transitions)."""
    global _STORE, _STORE_MISSING
    if _STORE is None and not _STORE_MISSING:
        try:
            z = np.load(GEK_ASSET, allow_pickle=False)
            vocab = [str(w) for w in z["vocab"].tolist()]
            _STORE = {
                "vocab": vocab,
                "wid": {w: i for i, w in enumerate(vocab)},
                "indptr": z["indptr"], "indices": z["indices"], "data": z["data"],
                "src": z["src_marg"], "tgt": z["tgt_marg"], "tf": float(z["tf"][0]),
            }
        except (FileNotFoundError, OSError, KeyError, ValueError):
            _STORE_MISSING = True
            _STORE = None
    return _STORE


def available() -> bool:
    """Whether the frozen GEK store is present (loads). False -> the readouts abstain, never raise."""
    return _store() is not None


def _ppmi(store: Dict, aid: int, cid: int) -> float:
    """Directed forward PPMI(a -> c), byte-faithful to exp_forward_event_projection_v1._ppmi over the CSR:
    max(0, log((j/tf) / ((src[a]/tf)*(tgt[c]/tf) + EPS) + EPS)); 0 when the pair was never seen."""
    lo = int(store["indptr"][aid]); hi = int(store["indptr"][aid + 1])
    if hi <= lo:
        return 0.0
    row = store["indices"][lo:hi]                       # a VIEW (sorted target ids) -- no copy
    p = lo + int(np.searchsorted(row, cid))
    if p >= hi or int(store["indices"][p]) != cid:
        return 0.0
    j = int(store["data"][p])
    tf = store["tf"]
    sc = int(store["src"][aid]); tc = int(store["tgt"][cid])
    return max(0.0, math.log((j / tf) / ((sc / tf) * (tc / tf) + _EPS) + _EPS))


@dataclass
class ForwardPrediction:
    """The glass-box trace of one forward projection (discrimination or generative). Additive read-only."""
    picked: Optional[int]                                   # argmax candidate index (discrimination), else None
    candidates: List[str] = field(default_factory=list)     # candidate surface forms scored (discrimination)
    scores: List[float] = field(default_factory=list)       # combined per-candidate activation (gek + goal)
    cue_scores: List[Dict[str, float]] = field(default_factory=list)  # per-candidate {"gek":..,"goal":..}
    precision: float = 0.0                                  # 1 - normalized entropy (distribution concentration)
    distribution: List[float] = field(default_factory=list) # softmax over candidates (native graded output)
    expected: List[Tuple[str, float]] = field(default_factory=list)   # generative top-k forward content
    abstained: bool = False                                 # nothing scorable / no asset
    source: str = "gek+goal"


class GEKProjector:
    """Forward generalized-event-knowledge projection over the frozen store. Stateless apart from the
    process-level store singleton -- one instance per reader is fine. Constructing it loads NOTHING; the
    store loads lazily on the first available()/score()/project() call."""

    GAIN = 2.0                                              # softmax gain (precision term; swept, not adopted)

    def available(self) -> bool:
        return available()

    def score(self, ctx_lemmas: Sequence[str], ending_lemmas: Sequence[str]) -> float:
        """The GEK content cue: mean over the ending's covered lemmas of the summed directed forward PPMI
        from each covered context lemma. Byte-faithful to exp_forward_event_projection_v1.make_scorer("fwd").
        0.0 when the store is absent, or the ending has no covered content."""
        store = _store()
        if store is None:
            return 0.0
        wid = store["wid"]
        el = [wid[e] for e in ending_lemmas if e in wid]
        if not el:
            return 0.0
        cl = [wid[c] for c in ctx_lemmas if c in wid]
        return sum(sum(_ppmi(store, a, e) for a in cl) for e in el) / len(el)

    def expected(self, ctx_lemmas: Sequence[str], topk: int = 8) -> List[Tuple[str, float]]:
        """Generative forward projection: the top-k forward-expected content tokens given the context =
        argmax_w sum_a PPMI(a -> w). Excludes context words themselves. [] if the store is absent or no
        context content is covered. NOT a validated capability -- offered glass-box for elaboration."""
        store = _store()
        if store is None:
            return []
        wid = store["wid"]
        cl = [wid[c] for c in ctx_lemmas if c in wid]
        if not cl:
            return []
        V = len(store["vocab"])
        acc = np.zeros(V, dtype=np.float64)
        for a in cl:
            lo = int(store["indptr"][a]); hi = int(store["indptr"][a + 1])
            for p in range(lo, hi):
                cid = int(store["indices"][p])
                acc[cid] += _ppmi(store, a, cid)
        ctxset = set(cl)
        out: List[Tuple[str, float]] = []
        for cid in np.argsort(-acc):
            cid = int(cid)
            if acc[cid] <= 0.0:
                break
            if cid in ctxset:
                continue
            out.append((store["vocab"][cid], float(acc[cid])))
            if len(out) >= topk:
                break
        return out

    def project(self, ctx_lemmas: Sequence[str], goal_lemmas: Sequence[str],
                candidate_bags: Sequence[Sequence[str]], *, gain: Optional[float] = None) -> Optional[ForwardPrediction]:
        """DISCRIMINATION readout: score each candidate continuation by the GEK content cue (context ->
        candidate) and the goal cue (agent goal text -> candidate), COMPOSE the two via graded_competition
        (equal weights on standardized cues -- OUR-INVENTION, not tuned), argmax = the forward-projected
        continuation, precision = 1 - normalized entropy. Returns a ForwardPrediction, or None when the store
        is absent or there is nothing to score (no candidates / all candidates uncovered = abstain)."""
        store = _store()
        if store is None or not candidate_bags:
            return None
        n = len(candidate_bags)
        gek = [self.score(ctx_lemmas, cb) for cb in candidate_bags]
        goal = [self.score(goal_lemmas, cb) if goal_lemmas else 0.0 for cb in candidate_bags]
        if not any(gek) and not any(goal):
            return None                                    # nothing covered -> abstain (never guess)
        g = float(self.GAIN if gain is None else gain)

        def _z(x: List[float]) -> np.ndarray:
            a = np.asarray(x, dtype=np.float64)
            return (a - a.mean()) / (a.std() + 1e-9)

        comb = (_z(gek) + _z(goal)) if n >= 2 else (np.asarray(gek) + np.asarray(goal))
        from hdlab.graded_competition import graded_pick
        gp = graded_pick({"cue": comb.tolist()}, {"cue": 1.0}, gain=g)
        precision = 1.0 - float(gp["entropy"])
        return ForwardPrediction(
            picked=int(np.argmax(comb)),
            candidates=[],                                 # filled by the caller with the surface forms
            scores=[float(v) for v in comb],
            cue_scores=[{"gek": float(gek[i]), "goal": float(goal[i])} for i in range(n)],
            precision=precision,
            distribution=[float(v) for v in np.asarray(gp["p"]).reshape(-1)],
            expected=[], abstained=False, source="gek+goal")

    def project_expected(self, ctx_lemmas: Sequence[str], *, topk: int = 8,
                         gain: Optional[float] = None) -> Optional[ForwardPrediction]:
        """Generative wrapper: the top-k forward-expected content as a ForwardPrediction (precision = 1 -
        normalized entropy of the softmax over the top-k scores). None if the store is absent."""
        store = _store()
        if store is None:
            return None
        exp = self.expected(ctx_lemmas, topk=topk)
        if not exp:
            return ForwardPrediction(picked=None, expected=[], precision=0.0, abstained=True, source="gek+goal")
        g = float(self.GAIN if gain is None else gain)
        from hdlab.graded_competition import graded_pick
        gp = graded_pick({"cue": [s for _, s in exp]}, {"cue": 1.0}, gain=g)
        return ForwardPrediction(
            picked=None, expected=exp, precision=1.0 - float(gp["entropy"]),
            distribution=[float(v) for v in np.asarray(gp["p"]).reshape(-1)],
            abstained=False, source="gek+goal")


# =========================================================================== OFFLINE BUILD (static asset)
def build_from_jsonl(path: str = ROC_JSONL, vocab_cap: int = VOCAB_CAP) -> Dict:
    """Fit the directed forward-transition store from a ROCStories-style jsonl (sentence1..sentence5).
    Byte-faithful to exp_forward_event_projection_v1.build_store (the "fwd" directed multi-step map: for a
    story, count every (content lemma in sentence i -> content lemma in sentence j>i) pair). OFFLINE ONLY.
    Returns {vocab, fwd, src, tgt, tf}."""
    import json
    from collections import Counter, defaultdict
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            rows.append(json.loads(line))
    uni: "Counter[str]" = Counter()
    all_bags = []
    for r in rows:
        bags = [lemmatize(r["sentence%d" % j]) for j in range(1, 6)]
        all_bags.append(bags)
        for b in bags:
            uni.update(set(b))
    vocab = {w for w, _ in uni.most_common(vocab_cap)}
    fwd: "defaultdict[str, Counter]" = defaultdict(Counter)
    src: "Counter[str]" = Counter()
    tgt: "Counter[str]" = Counter()
    tf = 0
    for bags in all_bags:
        bags = [sorted(set(w for w in b if w in vocab)) for b in bags]
        for i in range(len(bags)):
            for j in range(i + 1, len(bags)):
                for a in bags[i]:
                    for c in bags[j]:
                        fwd[a][c] += 1
                        src[a] += 1
                        tgt[c] += 1
                        tf += 1
    return {"vocab": sorted(vocab), "fwd": fwd, "src": src, "tgt": tgt, "tf": float(tf), "n_stories": len(rows)}


def freeze(built: Dict, path: str = GEK_ASSET) -> Dict:
    """Serialize a built store to the compact CSR npz asset (rows keyed by vocab id, target ids sorted per
    row for binary-search PPMI lookup). Atomic write. Returns a small summary dict."""
    vocab = list(built["vocab"])
    V = len(vocab)
    wid = {w: i for i, w in enumerate(vocab)}
    fwd = built["fwd"]
    indptr = np.zeros(V + 1, dtype=np.int64)
    indices: List[int] = []
    data: List[int] = []
    for a in range(V):
        row = fwd.get(vocab[a])
        if row:
            items = sorted((wid[c], int(cnt)) for c, cnt in row.items() if c in wid)
            for cid, cnt in items:
                indices.append(cid)
                data.append(cnt)
        indptr[a + 1] = len(indices)
    src_marg = np.array([int(built["src"].get(vocab[a], 0)) for a in range(V)], dtype=np.int64)
    tgt_marg = np.array([int(built["tgt"].get(vocab[a], 0)) for a in range(V)], dtype=np.int64)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp.npz"
    np.savez(tmp,
             vocab=np.array(vocab),
             indptr=indptr,
             indices=np.array(indices, dtype=np.int32),
             data=np.array(data, dtype=np.int32),
             src_marg=src_marg, tgt_marg=tgt_marg,
             tf=np.array([built["tf"]], dtype=np.float64))
    os.replace(tmp, path)
    return {"vocab": V, "nnz_pairs": len(indices), "tf": built["tf"],
            "n_stories": built.get("n_stories"), "path": path}


def _build_main() -> None:
    import time
    t0 = time.time()
    print("[gek] building forward-transition store from %s ..." % ROC_JSONL)
    built = build_from_jsonl()
    print("[gek] built vocab=%d fwd_src=%d tf=%.0f (%.1fs)"
          % (len(built["vocab"]), len(built["fwd"]), built["tf"], time.time() - t0))
    summary = freeze(built)
    sz = os.path.getsize(summary["path"]) / 1e6
    print("[gek] froze -> %s (%.1f MB, nnz_pairs=%d, %.1fs)"
          % (summary["path"], sz, summary["nnz_pairs"], time.time() - t0))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="fit + freeze the offline GEK store asset")
    a = ap.parse_args()
    if a.build:
        _build_main()
    else:
        st = _store()
        print("GEK store present: %s (%s)" % (available(), GEK_ASSET))
        if st is not None:
            print("  vocab=%d tf=%.0f nnz=%d" % (len(st["vocab"]), st["tf"], len(st["indices"])))
