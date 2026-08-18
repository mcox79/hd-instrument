"""PHASE-1 parser UAS-ladder: RICHER GLASS-BOX CLASSICAL FEATURES on the arc-scorer (Lever D).

GOAL: test whether the June-drill Lever-D residual -- richer STATIC glass-box classical features for the
  arc-scorer (CHAR-PREFIX/SUFFIX for OOV robustness + affix x POS-pair conjunction templates) -- lifts the
  persisted arc parser above UAS 0.7868 (greedy local-argmax + cycle-break, 1st-order hashed features). These
  are glass-box CLASSICAL features (NOT contextual embeddings, NOT an LLM), different in KIND from the already-
  tried decode (MST +0.0097) and syntactic-labeler levers. ONE VARIABLE = the arc-scorer FEATURE SET; the
  decode is held at GREEDY (identical to the 0.7868 baseline) so any delta is purely the added features.

CLASSICAL LADDER (June drill research_drill_dep_parse_0787_to_085_substrate_paths_2x_2026-06-11, Lever D):
  "Add char-prefix-4 + char-suffix-4 bundles for OOV robustness (8.5% OOV = the dominant residual error
   source) + POS-tag-of-head + POS-tag-of-modifier + POS-pair-conjunction ... the single highest-yield
   template family per McDonald 2005 ablations (POS-pair templates ~3-5 UAS absolute on PTB)."
  BASE_FEATS  = hdlab.arc_parser._arc_ids (21 templates; ALREADY has suffix-3-x-crossPOS + POS-pairs)  [0.7868]
  RICH_FEATS  = BASE_FEATS + {char prefix-3/4, suffix-2/4 (standalone, both head+dep), word-SHAPE (Xxxx/dddd),
                affix x POS-pair conjunction, affix x affix backoff, shape x POS-pair}  (monotone SUPERSET)
  Brown clusters DEFERRED (no clustering asset in-repo; would need a separate cheap-to-build Brown/word-class
   pass -- declared not-cheap-this-cell per the drill's "optionally Brown clusters if cheap"). See report.

ARMS (all GREEDY decode; ONE VARIABLE = feature fn):
  CANON      = persisted greedy 1st-order weights, eval-only (re-derives the REAL 0.7868 baseline LIVE)
  BASE_REFIT = baseline features, retrained with THIS harness (epochs/seed) -- controls for any harness drift
  RICH       = rich features, retrained with THIS harness -- the mechanism arm
  Primary delta = RICH - BASE_REFIT (pure feature effect, harness-matched) AND RICH vs CANON 0.7868.

KEY DIAGNOSTIC (the claimed mechanism): OOV-error reduction. Partition dev arcs by whether the DEPENDENT
  surface form is OOV (unseen in the train vocab); report UAS on OOV-dep arcs BASE_REFIT vs RICH. The Lever-D
  claim is that char-affix features lift precisely the OOV arcs. If RICH does NOT beat BASE_REFIT on OOV-dep
  arcs, the mechanism did not fire even where it should -- classical features are EMPIRICALLY tapped.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline = the persisted 0.7868 parser, greedy-decoded LIVE on UD-EWT dev (re-derived, not
      remembered) = CANON. Plus BASE_REFIT (baseline feats, matched harness) so the feature delta is clean.
  (2) CAN-FAIL (all informative): (a) richer features may NOT lift UAS on THIS 2^21 hashed codebook (the
      lit's PTB numbers did NOT transfer to MST here: MST was +0.0097 not the +2-3 PTB precedent -- same
      hashed-codebook + UD-EWT-web risk); (b) may lift on UD-EWT-web dev but NOT transfer to archaic McGuffey
      (that is the Cell-2 reader question, not this cell); (c) added templates increase hash COLLISIONS in the
      fixed 2^21 space and could NET-HURT. A within-noise / negative result EMPIRICALLY CONFIRMS classical
      LAS is tapped -- banks the stronger requires-better-representation bound (not merely hypothesized).
  (3) DIFFICULTY-ON = the OOV-dep arcs (dominant error source) surfaced as a dedicated partition; full UD-EWT
      dev (1989 sents) eval.
  (4) ONE-VARIABLE = the feature function. Same greedy decode, same epochs/seed/maxlen across BASE_REFIT/RICH.

VERDICT BANDS (pre-registered; MEASUREMENT cell -- primary deliverable = the UAS numbers + the OOV partition):
  RICHFEAT_LIFT_REAL:   RICH >= max(CANON, BASE_REFIT) + 0.005  (a real classical-feature lift; > ~0.792).
  RICHFEAT_FLAT_TAPPED:  |RICH - max(CANON, BASE_REFIT)| < 0.005 (classical features EMPIRICALLY tapped on
                        this codebook -- the requires-better-representation conclusion is then SUPPORTED, not
                        merely hypothesized).
  RICHFEAT_REGRESS:     RICH < max(CANON, BASE_REFIT) - 0.005   (hash-collision cost dominates the added
                        signal; the fixed 2^21 space is saturated).

LEAK-HUNT (in-cell): (1) features are SURFACE char/POS/position only, computed IDENTICALLY for the gold head
  and every competing candidate head (the gold HEAD INDEX is the LABEL and never enters a feature) -- so no
  feature can encode gold-ness (asserted in self_test: dependent-side features are head-invariant). (2) UD-EWT
  train/dev split respected: train on train, eval UAS on dev; OOV vocab computed from TRAIN only. (3) giveaway
  audit: over a dev sample, no single feature id present in the gold arc is absent from ALL competing candidate
  arcs (a perfect separator would be a leak) -- report max single-feature gold-vs-competitor separation.

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified: pure-python averaged perceptron, greedy O(n^2)
  decode; UD-EWT avg len ~16 -> trivial. MEASURED calib: baseline 800x3ep=5.4s -> full 12329x10ep ~4.6min,
  rich ~1.7x feature count ~ ~9-10min; full-dev eval ~7s). Storage: no_storage (persists a weight vector, not
  substrate atoms). progress_logging: print_flush_true (long full mode). Determinism: fixed int seed, numpy
  default_rng, sorted iteration; NO hash()-seeded RNG. LOCAL-ONLY; NO queue, NO push, NO remote-persist, NO
  substrate store write, NO git add.

CELL-TEMPLATE: except SystemExit: raise BEFORE except Exception (no BaseException); atomic tmp_replace metrics;
  arms_differ (BASE_REFIT vs RICH weights bit-differ); baseline_in_band; all numbers tagged MEASURED@/CITED@.

PRIOR-WORK CHECK (substrate_query.sh "arc parser dependency LAS features char prefix suffix POS pair
  conjunction Brown clusters structured perceptron UD-EWT"): top hit cosine=0.2988 (the June Lever-D drill
  note itself) -- BELOW the 0.30 bar; NO prior CELL added char-affix/word-shape features to the arc scorer.
  The tried siblings were DECODE (MST, exp_parser_uas_ladder_mst_retrain_v1) and LABELER-syntactic features,
  NOT arc-scorer static features. Genuine build of the drill's Lever D. CITED@drill 2026-06-11.

NO LLM. numpy + pure-python only. ASCII-only.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments"))

from hdlab.arc_parser import ArcParser, _arc_ids, _h, _dist, SIZE  # noqa: E402
from _ud_loader import load_conllu  # noqa: E402

ANCHOR_NAME = "parser_uas_ladder_richfeat_v1"
FRONTEND_DIR = REPO / "data" / "frontend_assets"
CANON_ARC = FRONTEND_DIR / "arc_parser_hashed_ud_ewt.npz"          # BASE greedy 1st-order (0.7868)
RICH_ARC = FRONTEND_DIR / "arc_parser_richfeat_ud_ewt.npz"         # persisted RICH parser (this cell, full only)
OUT_DIR = REPO / "data" / f"exp_{ANCHOR_NAME}"

BASELINE_UAS = 0.7868  # MEASURED@data/exp_depparse_hashed_cpu_v1/metrics.json + re-derived live below (CANON)


# ================================================================================================
# RICH feature function: baseline ids (monotone) PLUS char-affix / word-shape / affix x POS-pair templates.
# ALL surface-only (char/POS/position); the gold head index is the LABEL and never enters a feature.
# ================================================================================================
def _pre(w: str, k: int) -> str:
    return w[:k] if len(w) >= k else w


def _sufk(w: str, k: int) -> str:
    return w[-k:] if len(w) >= k else w


def _shape(w: str) -> str:
    """Collapsed word-shape: upper->X lower->x digit->d else literal; runs collapsed (Xxxx dddd)."""
    out = []
    prev = ""
    for c in w:
        if c.isupper():
            s = "X"
        elif c.islower():
            s = "x"
        elif c.isdigit():
            s = "d"
        else:
            s = c
        if s != prev:
            out.append(s)
            prev = s
    return "".join(out) if out else "_"


def _rich_extra_feats(sent: Sequence[tuple], i: int, h: int) -> List[str]:
    """New surface feature STRINGS added on top of baseline _arc_ids (head-side + dependent-side; no gold)."""
    n = len(sent)
    d_form = sent[i - 1][1]
    dw, dp = d_form.lower(), sent[i - 1][2]
    if h == 0:
        h_form, hw, hp = "<ROOT>", "<ROOT>", "ROOT"
        d = 0
        dr = "R"
    else:
        h_form = sent[h - 1][1]
        hw, hp = h_form.lower(), sent[h - 1][2]
        d = h - i
        dr = "L" if d < 0 else "R"
    db = _dist(d)
    ds4, ds2 = _sufk(dw, 4), _sufk(dw, 2)
    dp4, dp3 = _pre(dw, 4), _pre(dw, 3)
    hs4 = _sufk(hw, 4)
    hp4 = _pre(hw, 4)
    dsh, hsh = _shape(d_form), _shape(h_form)
    F = [
        # dependent-side char-affix backoff (OOV robustness; head-INVARIANT except db/dr)
        "R_dpre4:" + dp4, "R_dpre3:" + dp3, "R_dsuf4:" + ds4, "R_dsuf2:" + ds2,
        # head-side char-affix backoff
        "R_hpre4:" + hp4, "R_hsuf4:" + hs4,
        # word-shape (capitalization/digit signature; strong OOV/proper-noun cue)
        "R_dshape:" + dsh, "R_hshape:" + hsh,
        # affix x POS-pair conjunction (richer McDonald-style POS-pair, OOV-lexicalized)
        "R_dsuf4_hp_dp:%s_%s_%s" % (ds4, hp, dp), "R_hsuf4_hp_dp:%s_%s_%s" % (hs4, hp, dp),
        # affix x affix backoff (OOV backoff of the lexical hw_dw bigram)
        "R_hsuf4_dsuf4:%s_%s" % (hs4, ds4),
        # shape x POS-pair
        "R_dshape_hp_dp:%s_%s_%s" % (dsh, hp, dp),
        # dependent affix x direction x distance-bucket
        "R_dsuf4_dir_dist:%s_%s_%s" % (ds4, dr, db),
    ]
    return F


def _arc_ids_rich(sent: Sequence[tuple], i: int, h: int) -> np.ndarray:
    """Baseline hashed ids (verbatim) concatenated with rich extra hashed ids. Monotone superset of _arc_ids."""
    base = _arc_ids(sent, i, h)
    extra = np.fromiter((_h(f) for f in _rich_extra_feats(sent, i, h)),
                        dtype=np.int64, count=len(_rich_extra_feats(sent, i, h)))
    return np.concatenate([base, extra])


# ================================================================================================
# RichArcParser: drop-in for hdlab.arc_parser.ArcParser (greedy decode + cycle-break + per-arc margins),
# but scores with the RICH feature function. Same npz format + parse()->ParseResult interface so the reader
# (Cell 2) swaps ONLY the parser. Margins = greedy head-score best-second (the abstain signal).
# ================================================================================================
from typing import NamedTuple


class ParseResult(NamedTuple):
    arcs: List[Tuple[int, int]]
    margins: Dict[int, float]
    heads: Dict[int, int]


class RichArcParser:
    """Greedy arc parser using the RICH feature fn; matches ArcParser.parse/eval_uas/save/load interface."""

    def __init__(self, avg: np.ndarray):
        self.avg = np.asarray(avg, dtype=np.float64)

    @classmethod
    def load(cls, path: str) -> "RichArcParser":
        with np.load(path) as z:
            return cls(z["avg"].astype(np.float64))

    def save(self, path: str) -> None:
        np.savez_compressed(path, avg=self.avg.astype(np.float32))

    def _arc_and_score(self, sent):
        n = len(sent)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h != i:
                    arc[i][h] = _arc_ids_rich(sent, i, h)
        return arc

    def parse(self, tokens: Sequence[str], pos_tags: Sequence[str]) -> ParseResult:
        if len(tokens) != len(pos_tags):
            raise ValueError("tokens (%d) and pos_tags (%d) length mismatch" % (len(tokens), len(pos_tags)))
        sent = [(k + 1, tokens[k], pos_tags[k], 0, "_") for k in range(len(tokens))]
        n = len(sent)
        if n == 0:
            return ParseResult([], {}, {})
        arc = self._arc_and_score(sent)
        head = _greedy_heads(self.avg, arc, n)
        margins: Dict[int, float] = {}
        for i in range(1, n + 1):
            col = sorted((float(self.avg[arc[i][h]].sum()) for h in range(0, n + 1) if h != i), reverse=True)
            margins[i] = float(col[0] - (col[1] if len(col) > 1 else col[0]))
        arcs = [(head.get(i, 0), i) for i in range(1, n + 1)]
        return ParseResult(arcs=arcs, margins=margins, heads=head)

    def eval_uas(self, dev_sents, maxlen: int = 50):
        return eval_uas(self.avg, dev_sents, _arc_ids_rich, maxlen)


# ================================================================================================
# Greedy decode + averaged-perceptron train PARAMETRIZED by the feature function (one-variable control).
# _decode/eval are greedy local-argmax + cycle-break, verbatim in behaviour to hdlab.arc_parser.
# ================================================================================================
def _precompute(sents: Sequence[Sequence[tuple]], feat_fn) -> list:
    out = []
    for s in sents:
        n = len(s)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h != i:
                    arc[i][h] = feat_fn(s, i, h)
        out.append(arc)
    return out


def _greedy_heads(avg: np.ndarray, arc: list, n: int) -> Dict[int, int]:
    S: Dict[int, Dict[int, float]] = {}
    head: Dict[int, int] = {}
    for i in range(1, n + 1):
        cand = []
        for h in range(0, n + 1):
            if h == i:
                continue
            cand.append((float(avg[arc[i][h]].sum()), h))
        cand.sort(reverse=True)
        head[i] = cand[0][1]
        S[i] = {h: sc for sc, h in cand}
    for _ in range(n + 2):
        cyc = None
        for start in range(1, n + 1):
            seen = []
            x = start
            while x != 0 and x not in seen:
                seen.append(x)
                x = head[x]
            if x != 0:
                cyc = seen[seen.index(x):]
                break
        if cyc is None:
            break
        best_node = best_alt = None
        best_loss = 1e18
        cset = set(cyc)
        for node in cyc:
            cur = S[node][head[node]]
            alt_h, alt_s = -1, -1e18
            for hh, sc in S[node].items():
                if hh not in cset and sc > alt_s:
                    alt_s, alt_h = sc, hh
            if alt_h >= 0 and (cur - alt_s) < best_loss:
                best_loss, best_node, best_alt = cur - alt_s, node, alt_h
        if best_node is None:
            break
        head[best_node] = best_alt
    return head


def train_greedy(train, feat_fn, epochs, seed=1027):
    """Averaged perceptron, greedy decode in the loop (same algorithm as hdlab.arc_parser.train_arc)."""
    rng = np.random.default_rng(seed)
    tr_arc = _precompute(train, feat_fn)
    W = np.zeros(SIZE)
    CW = np.zeros(SIZE)
    c = 1
    for ep in range(epochs):
        te = time.time()
        for si in rng.permutation(len(train)):
            s = train[si]
            arc = tr_arc[si]
            n = len(s)
            for i in range(1, n + 1):
                gh = s[i - 1][3]
                if gh < 0 or gh > n:
                    continue
                best_h, best_s = -1, -1e18
                for h in range(0, n + 1):
                    if h == i:
                        continue
                    sc = W[arc[i][h]].sum()
                    if sc > best_s:
                        best_s, best_h = sc, h
                if best_h != gh:
                    np.add.at(W, arc[i][gh], 1.0)
                    np.add.at(CW, arc[i][gh], c)
                    np.add.at(W, arc[i][best_h], -1.0)
                    np.add.at(CW, arc[i][best_h], -c)
                c += 1
        print("[%s] train ep %d done %.1fs" % (ANCHOR_NAME, ep + 1, time.time() - te), flush=True)
    return W - CW / c


def eval_uas(avg, dev, feat_fn, maxlen=50):
    dev = [s for s in dev if 1 <= len(s) <= maxlen]
    corr = tot = 0
    for s in dev:
        n = len(s)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h != i:
                    arc[i][h] = feat_fn(s, i, h)
        head = _greedy_heads(avg, arc, n)
        for i in range(1, n + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > n:
                continue
            corr += int(head.get(i, -1) == gh)
            tot += 1
    return (corr / tot if tot else 0.0, corr, tot)


def eval_uas_oov(avg, dev, feat_fn, train_vocab, maxlen=50):
    """UAS split by whether the DEPENDENT surface form is OOV (unseen in train_vocab). Returns (oov, iv) tuples."""
    dev = [s for s in dev if 1 <= len(s) <= maxlen]
    oc = ot = ic = it = 0
    for s in dev:
        n = len(s)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h != i:
                    arc[i][h] = feat_fn(s, i, h)
        head = _greedy_heads(avg, arc, n)
        for i in range(1, n + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > n:
                continue
            ok = int(head.get(i, -1) == gh)
            if s[i - 1][1].lower() in train_vocab:
                ic += ok
                it += 1
            else:
                oc += ok
                ot += 1
    return ((oc / ot if ot else 0.0, oc, ot), (ic / it if it else 0.0, ic, it))


def build_vocab(train):
    v = set()
    for s in train:
        for tok in s:
            v.add(tok[1].lower())
    return v


def giveaway_audit(dev, feat_fn, n_sample=200, seed=1027):
    """Max single-feature separation: over sampled arcs, fraction of gold-arc features NOT in ANY competitor.
    A feature perfectly separating gold from all competitors on every arc would be a leak. Report the max."""
    rng = np.random.default_rng(seed)
    dev = [s for s in dev if 2 <= len(s) <= 40]
    idx = rng.permutation(len(dev))[:n_sample]
    max_uniq_frac = 0.0
    worst = None
    for j in idx:
        s = dev[int(j)]
        n = len(s)
        for i in range(1, n + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > n or gh == i:
                continue
            gold_ids = set(int(x) for x in feat_fn(s, i, gh))
            comp = set()
            for h in range(0, n + 1):
                if h == i or h == gh:
                    continue
                comp.update(int(x) for x in feat_fn(s, i, h))
            uniq = gold_ids - comp  # gold features not shared by ANY competitor
            frac = len(uniq) / max(1, len(gold_ids))
            if frac > max_uniq_frac:
                max_uniq_frac = frac
                worst = {"sid_len": n, "dep": s[i - 1][1], "gold_head": gh, "uniq_frac": round(frac, 3)}
    return {"max_gold_unique_feature_frac": round(max_uniq_frac, 4), "worst_arc": worst,
            "note": "surface features (dist/dir/head-side) legitimately vary by head; frac<1 => no perfect "
                    "single-feature gold separator (structural, expected)."}


def _cfg(smoke):
    if smoke:
        return {"n_train": 3000, "epochs": 5, "maxlen": 50}
    return {"n_train": None, "epochs": 10, "maxlen": 50}


def self_test():
    print("=== %s self-test (real code paths) ===" % ANCHOR_NAME, flush=True)
    toy = [(1, "The", "DET", 2, "det"), (2, "Cats", "NOUN", 3, "nsubj"),
           (3, "ran", "VERB", 0, "root"), (4, ".", "PUNCT", 3, "punct")]
    # (1) rich = monotone superset of baseline (baseline ids are a prefix of rich ids).
    b = _arc_ids(toy, 2, 3)
    r = _arc_ids_rich(toy, 2, 3)
    assert len(r) > len(b) and np.array_equal(r[:len(b)], b), "rich must be baseline-superset"
    print("[selftest] rich superset OK: base=%d rich=%d feats" % (len(b), len(r)), flush=True)
    # (2) LEAK: dependent-side rich features are HEAD-INVARIANT (the gold head index does not enter a
    #     dependent feature). Compare rich extras for two different candidate heads; the dep prefix/suffix/
    #     shape features (R_dpre*/R_dsuf*/R_dshape) must be identical across heads.
    ex_g = _rich_extra_feats(toy, 2, 3)
    ex_o = _rich_extra_feats(toy, 2, 1)
    _dep_keys = ("R_dpre4:", "R_dpre3:", "R_dsuf4:", "R_dsuf2:", "R_dshape:")  # purely dependent-side (exact)
    dep_only_g = [f for f in ex_g if f.startswith(_dep_keys)]
    dep_only_o = [f for f in ex_o if f.startswith(_dep_keys)]
    assert dep_only_g == dep_only_o, ("dependent-side features must be head-invariant (no gold leak)",
                                      dep_only_g, dep_only_o)
    print("[selftest] leak-guard OK: dependent affix/shape features head-invariant", flush=True)
    # (3) word-shape sanity.
    assert _shape("Xi2Foo") and _shape("Cat") == "Xx" and _shape("2019") == "d", _shape("2019")
    # (4) train+eval on a tiny slice actually runs (real greedy perceptron path).
    tr = [s for s in load_conllu("train") if 2 <= len(s) <= 20][:40]
    dv = [s for s in load_conllu("dev") if 2 <= len(s) <= 20][:40]
    avg = train_greedy(tr, _arc_ids_rich, epochs=1)
    u = eval_uas(avg, dv, _arc_ids_rich)[0]
    assert 0.0 <= u <= 1.0
    print("[selftest] real train+eval OK: tiny rich uas=%.3f" % u, flush=True)
    print("[selftest] PASS", flush=True)
    return True


def run(smoke: bool):
    t0 = time.time()
    cfg = _cfg(smoke)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train = [s for s in load_conllu("train") if 1 <= len(s) <= cfg["maxlen"]]
    dev = [s for s in load_conllu("dev") if 1 <= len(s) <= cfg["maxlen"]]
    if cfg["n_train"]:
        train = train[:cfg["n_train"]]
    vocab = build_vocab(train)
    print("[%s] train=%d dev=%d smoke=%s vocab=%d" % (ANCHOR_NAME, len(train), len(dev), smoke, len(vocab)),
          flush=True)

    # CANON: re-derive the REAL 0.7868 baseline (greedy decode on persisted weights, baseline features).
    canon = ArcParser.load(str(CANON_ARC))
    canon_uas, cc, ct = canon.eval_uas(dev)
    print("[%s] CANON persisted greedy baseline dev UAS=%.4f (%d/%d)" % (ANCHOR_NAME, canon_uas, cc, ct),
          flush=True)

    # BASE_REFIT: baseline features, THIS harness (controls for harness drift vs CANON).
    print("[%s] training BASE_REFIT (baseline feats)..." % ANCHOR_NAME, flush=True)
    base_avg = train_greedy(train, _arc_ids, cfg["epochs"])
    base_uas, bc, bt = eval_uas(base_avg, dev, _arc_ids)
    print("[%s] BASE_REFIT dev UAS=%.4f (%d/%d)" % (ANCHOR_NAME, base_uas, bc, bt), flush=True)

    # RICH: rich features, same harness (the mechanism arm).
    print("[%s] training RICH (rich feats)..." % ANCHOR_NAME, flush=True)
    rich_avg = train_greedy(train, _arc_ids_rich, cfg["epochs"])
    rich_uas, rc, rt = eval_uas(rich_avg, dev, _arc_ids_rich)
    print("[%s] RICH dev UAS=%.4f (%d/%d)" % (ANCHOR_NAME, rich_uas, rc, rt), flush=True)

    # OOV partition (the claimed mechanism): does RICH beat BASE_REFIT on OOV-dependent arcs?
    base_oov, base_iv = eval_uas_oov(base_avg, dev, _arc_ids, vocab)
    rich_oov, rich_iv = eval_uas_oov(rich_avg, dev, _arc_ids_rich, vocab)
    oov_delta = round(rich_oov[0] - base_oov[0], 4)
    iv_delta = round(rich_iv[0] - base_iv[0], 4)
    print("[%s] OOV-dep UAS base=%.4f rich=%.4f (delta=%+.4f, n_oov=%d) | IV base=%.4f rich=%.4f (delta=%+.4f)"
          % (ANCHOR_NAME, base_oov[0], rich_oov[0], oov_delta, base_oov[2], base_iv[0], rich_iv[0], iv_delta),
          flush=True)

    give = giveaway_audit(dev, _arc_ids_rich)

    ref = max(canon_uas, base_uas)
    delta_vs_ref = round(rich_uas - ref, 4)
    delta_vs_base_refit = round(rich_uas - base_uas, 4)
    delta_vs_canon = round(rich_uas - canon_uas, 4)

    if rich_uas >= ref + 0.005:
        verdict = "RICHFEAT_LIFT_REAL"
    elif rich_uas >= ref - 0.005:
        verdict = "RICHFEAT_FLAT_TAPPED"
    else:
        verdict = "RICHFEAT_REGRESS"

    # Persist the RICH parser ONLY in full mode (so Cell-2 reader-swap can load it). Uses a rich-aware
    # wrapper class in the reader-swap cell; here we store the raw averaged weights (npz, float32).
    persisted = None
    if not smoke:
        FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(str(RICH_ARC), avg=rich_avg.astype(np.float32))
        persisted = str(RICH_ARC)
        print("[%s] persisted RICH parser -> %s" % (ANCHOR_NAME, RICH_ARC), flush=True)

    arms_differ = bool(np.array_equal(base_avg, rich_avg) is False)
    baseline_in_band = bool(0.05 < canon_uas < 0.95)

    msg = ("%s | CANON=%.4f BASE_REFIT=%.4f RICH=%.4f | delta RICH-ref=%+.4f (ref=max(canon,base_refit)) "
           "RICH-base_refit=%+.4f RICH-canon=%+.4f | OOV-dep base=%.4f rich=%.4f (delta=%+.4f n=%d) "
           "| giveaway_max_uniq=%.3f | arms_differ=%s baseline_in_band=%s" %
           (verdict, canon_uas, base_uas, rich_uas, delta_vs_ref, delta_vs_base_refit, delta_vs_canon,
            base_oov[0], rich_oov[0], oov_delta, base_oov[2], give["max_gold_unique_feature_frac"],
            arms_differ, baseline_in_band))

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": ("smoke" if smoke else "full"),
        "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(time.time() - t0, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_train": len(train), "n_dev": len(dev), "n_train_vocab": len(vocab), "epochs": cfg["epochs"],
        "canon_uas": round(canon_uas, 4), "base_refit_uas": round(base_uas, 4), "rich_uas": round(rich_uas, 4),
        "delta_rich_vs_ref": delta_vs_ref, "delta_rich_vs_base_refit": delta_vs_base_refit,
        "delta_rich_vs_canon": delta_vs_canon, "ref_uas": round(ref, 4),
        "oov_dep_uas": {"base_refit": round(base_oov[0], 4), "rich": round(rich_oov[0], 4),
                        "delta": oov_delta, "n_oov_arcs": base_oov[2]},
        "iv_dep_uas": {"base_refit": round(base_iv[0], 4), "rich": round(rich_iv[0], 4),
                       "delta": iv_delta, "n_iv_arcs": base_iv[2]},
        "giveaway_audit": give,
        "canon_baseline_uas_cited": BASELINE_UAS,
        "brown_clusters": "DEFERRED_no_asset (declared not-cheap-this-cell per drill Lever D)",
        "rich_feature_families": ["char_prefix_3_4", "char_suffix_2_4_standalone", "word_shape",
                                  "affix_x_POSpair", "affix_x_affix", "shape_x_POSpair", "affix_dir_dist"],
        "persisted_rich_parser_path": persisted,
        "arms_differ_verified": arms_differ, "baseline_in_band": baseline_in_band,
        "compute_architecture": "sequential-CPU (justified)", "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True, "progress_logging": "print_flush_true", "one_variable": "feature_fn",
    }
    tmp = OUT_DIR / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, OUT_DIR / "metrics.json")
    print("[%s] DONE %.1fs -> %s" % (ANCHOR_NAME, time.time() - t0, verdict), flush=True)
    print(msg, flush=True)
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(smoke=args.smoke)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUT_DIR / "metrics.json.tmp", "w", encoding="utf-8") as f:
            json.dump({"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                       "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:400]),
                       "summary": "CELL_CRASHED", "elapsed_s": 0.0,
                       "traceback": traceback.format_exc()[:5000]}, f, indent=2)
        os.replace(OUT_DIR / "metrics.json.tmp", OUT_DIR / "metrics.json")
        raise
