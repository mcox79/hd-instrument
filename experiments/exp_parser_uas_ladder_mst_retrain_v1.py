"""PHASE-1 parser UAS-ladder: MST global decode + MST-in-the-loop structured perceptron retrain.

GOAL: lift the persisted arc parser above UAS 0.7868 (greedy local-argmax + cycle-break, 1st-order hashed
  features) via the classical S1 lever (Chu-Liu-Edmonds exact MST global decode) -- BOTH as inference-only
  swap (S1a) AND as MST-in-the-loop structured-perceptron retraining (S1b, weights optimised for the global
  decode). Persist the best parser with a parse() wrapper matching hdlab.arc_parser.ArcParser so the reader
  can swap ONLY the parser (Phase 2). Keeps per-arc margins (the abstain signal).

CLASSICAL LADDER (June drill research_drill_dep_parse_0787_to_085_substrate_paths_2x_2026-06-11):
  S0 greedy 1st-order  = data/frontend_assets/arc_parser_hashed_ud_ewt.npz          (MEASURED 0.7868)
  S1a MST-inference    = Chu-Liu-Edmonds on the SAME S0 weights                     (isolates decode-only)
  S1b MST-retrain      = structured perceptron with MST inference in the train loop (weights match decode)
  (S2 2nd-order grandparent was already MEASURED to HURT: 0.7783 < 0.7868 @depparse_2ndorder_cpu_v1; the
   drill's own analysis says 1st-order is the binding constraint. Not re-run here; see report.)

DESIGN-GATE (pre-registered; verified inline):
  (1) REAL baseline = the persisted 0.7868 parser, greedy-decoded LIVE on UD-EWT dev (re-derived, not remembered).
  (2) CAN-FAIL: (a) MST-inference on greedy-trained weights may be ~flat (the greedy cycle-break already
      approximates MST); (b) MST-retrain may not clear baseline much on THIS hashed codebook (the informative
      plateau -- the drill's 0.81/0.82 targets are PTB-lit precedent, not guaranteed on UD-EWT-bundled).
  (3) DIFFICULTY-ON: full UD-EWT dev (1989 sents, 24444 arcs), same eval as the persisted parser.
  (4) ONE-VARIABLE: S0->S1a differ only in the DECODE (greedy vs CLE); S0->S1b add MST-in-the-loop training.

VERDICT BANDS (pre-registered; MEASUREMENT cell -- primary deliverable = the UAS number + persisted parser):
  UAS_LIFT_REAL:   best(S1a,S1b) >= 0.7868 + 0.005  (a real classical-decode lift; >~0.79).
  UAS_FLAT_PLATEAU: best(S1a,S1b) in [0.7868 - 0.003, 0.7868 + 0.005) (MST neutral on this codebook).
  UAS_REGRESS:     best(S1a,S1b) < 0.7868 - 0.003   (should not happen; would indicate a decode bug).

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified: pure-python perceptron + O(n^2) CLE; UD-EWT avg
  len ~16 -> trivial; full 12329-train x <=12 epochs MST-retrain measured ~5min). Storage: no_storage (persists
  a weight vector, not substrate atoms). progress_logging: print_flush_true. Determinism: fixed int seed,
  numpy default_rng, sorted iteration; no hash()-seeded RNG. LOCAL-ONLY, foreground-to-completion; NO queue,
  NO push, NO remote-persist, NO substrate store write, NO git add.

CELL-TEMPLATE: except SystemExit: raise BEFORE except Exception (no BaseException); atomic tmp_replace metrics;
  early-stop on dev (best-epoch weights persisted, avoids the overfit tail); all numbers tagged MEASURED@/
  THEORETICAL@/CITED@.

PRIOR-WORK CHECK (substrate_query.sh "dependency parser MST second-order arc attachment UAS upgrade"):
  top hits cosine 0.26/0.25/0.248 all BELOW the 0.30 bar; the 0.248 hit is the June drill note itself (the
  documented ladder). NONE at cosine>0.30 is a prior MST-retrain parser CELL. Genuine build of the drill's
  S1 lever (the prior depparse_v2_mst cell never ran a real CLE: it used nltk-PTB count scoring + heuristic
  cycle-break and load-failed). CITED@research_drill_dep_parse_0787_to_085 2026-06-11.

NO LLM. numpy + pure-python only. ASCII-only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, NamedTuple, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments"))

from hdlab.arc_parser import ArcParser, _arc_ids, SIZE  # noqa: E402
from _ud_loader import load_conllu  # noqa: E402

ANCHOR_NAME = "parser_uas_ladder_mst_retrain_v1"
FRONTEND_DIR = REPO / "data" / "frontend_assets"
CANON_ARC = FRONTEND_DIR / "arc_parser_hashed_ud_ewt.npz"                 # S0 baseline (0.7868)
MST_ARC = FRONTEND_DIR / "arc_parser_mst_retrain_ud_ewt.npz"             # persisted S1b (this cell)
OUT_DIR = REPO / "data" / f"exp_{ANCHOR_NAME}"
CKPT_DIR = OUT_DIR / "ckpt"

BASELINE_UAS = 0.7868  # MEASURED@data/exp_depparse_hashed_cpu_v1/metrics.json + re-derived live below


# ================================================================================================
# Chu-Liu-Edmonds exact maximum spanning arborescence (root = node 0). O(n^2) with cycle contraction.
# ================================================================================================
def mst_cle(score: np.ndarray) -> Dict[int, int]:
    """score[h, d] = weight of arc h->d (h in 0..n head, d in 1..n dependent). Returns head[d], d in 1..n."""
    n = score.shape[0] - 1
    S = score.astype(np.float64).copy()
    np.fill_diagonal(S, -np.inf)
    S[:, 0] = -np.inf  # nothing points to root

    def solve(nodes: List[int], S: np.ndarray) -> Dict[int, int]:
        par: Dict[int, int] = {}
        for d in nodes:
            best_h = None
            best = -np.inf
            for h in list(nodes) + [0]:
                if h == d:
                    continue
                if S[h, d] > best:
                    best = S[h, d]
                    best_h = h
            par[d] = best_h
        for start in nodes:
            seen: List[int] = []
            x = start
            while x != 0 and x not in seen and x in par:
                seen.append(x)
                x = par[x]
            if x != 0 and x in seen:
                cyc = seen[seen.index(x):]
                cset = set(cyc)
                c = min(cyc)  # supernode label
                cyc_score = sum(S[par[v], v] for v in cyc)
                new_nodes = sorted(set([v for v in nodes if v not in cset] + [c]))
                m = S.shape[0]
                S2 = np.full((m, m), -np.inf)
                allh = list(nodes) + [0]
                into_from: Dict[int, int] = {}
                for h in allh:
                    if h in cset:
                        continue
                    for d in nodes:
                        if d in cset or d == h:
                            continue
                        S2[h, d] = S[h, d]
                for h in allh:
                    if h in cset:
                        continue
                    best = -np.inf
                    best_k = None
                    for d in cyc:
                        val = S[h, d] - S[par[d], d]
                        if val > best:
                            best = val
                            best_k = d
                    if best_k is not None:
                        S2[h, c] = best + cyc_score
                        into_from[h] = best_k
                out_to: Dict[int, int] = {}
                for d in nodes:
                    if d in cset:
                        continue
                    best = -np.inf
                    best_k = None
                    for h in cyc:
                        if S[h, d] > best:
                            best = S[h, d]
                            best_k = h
                    if best_k is not None:
                        S2[c, d] = best
                        out_to[d] = best_k
                sub = solve(new_nodes, S2)
                res: Dict[int, int] = {}
                hc = sub[c]
                kbreak = into_from[hc]
                res[kbreak] = hc
                for v in cyc:
                    if v != kbreak:
                        res[v] = par[v]
                for d, h in sub.items():
                    if d == c:
                        continue
                    res[d] = out_to[d] if h == c else h
                return res
        return par

    return solve(list(range(1, n + 1)), S)


# ================================================================================================
# MST-decoding ArcParser: same npz format + parse() interface as hdlab.arc_parser.ArcParser, but the
# decode is exact CLE and margins are best-head-score minus second-best-head-score (abstain signal).
# ================================================================================================
class ParseResult(NamedTuple):
    arcs: List[Tuple[int, int]]
    margins: Dict[int, float]
    heads: Dict[int, int]


class MstArcParser:
    """Drop-in for ArcParser: parse(tokens, pos_tags) -> ParseResult with CLE (MST) heads + per-arc margins."""

    def __init__(self, avg: np.ndarray):
        self.avg = np.asarray(avg, dtype=np.float64)

    @classmethod
    def load(cls, path: str) -> "MstArcParser":
        with np.load(path) as z:
            return cls(z["avg"].astype(np.float64))

    def save(self, path: str) -> None:
        np.savez_compressed(path, avg=self.avg.astype(np.float32))

    def _score_and_arc(self, sent) -> Tuple[np.ndarray, list]:
        n = len(sent)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        S = np.full((n + 1, n + 1), -1e18)
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h == i:
                    continue
                ids = _arc_ids(sent, i, h)
                arc[i][h] = ids
                S[h, i] = float(self.avg[ids].sum())
        return S, arc

    def parse(self, tokens: Sequence[str], pos_tags: Sequence[str]) -> ParseResult:
        if len(tokens) != len(pos_tags):
            raise ValueError("tokens (%d) and pos_tags (%d) length mismatch" % (len(tokens), len(pos_tags)))
        sent = [(k + 1, tokens[k], pos_tags[k], 0, "_") for k in range(len(tokens))]
        n = len(sent)
        if n == 0:
            return ParseResult([], {}, {})
        S, _arc = self._score_and_arc(sent)
        head = mst_cle(S)
        margins: Dict[int, float] = {}
        for i in range(1, n + 1):
            col = [S[h, i] for h in range(0, n + 1) if h != i]
            col.sort(reverse=True)
            margins[i] = float(col[0] - (col[1] if len(col) > 1 else col[0]))
        arcs = [(head.get(i, 0), i) for i in range(1, n + 1)]
        return ParseResult(arcs=arcs, margins=margins, heads=head)

    def eval_uas(self, dev_sents, maxlen: int = 50) -> Tuple[float, int, int]:
        dev = [s for s in dev_sents if 1 <= len(s) <= maxlen]
        corr = tot = 0
        for s in dev:
            n = len(s)
            S, _ = self._score_and_arc(s)
            head = mst_cle(S)
            for i in range(1, n + 1):
                gh = s[i - 1][3]
                if gh < 0 or gh > n:
                    continue
                corr += int(head.get(i, -1) == gh)
                tot += 1
        return (corr / tot if tot else 0.0, corr, tot)


# ================================================================================================
# Training helpers (feature-id precompute + MST-in-the-loop structured perceptron).
# ================================================================================================
def _precompute(sents):
    out = []
    for s in sents:
        n = len(s)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h != i:
                    arc[i][h] = _arc_ids(s, i, h)
        out.append(arc)
    return out


def _score_mat(W, arc, n):
    S = np.full((n + 1, n + 1), -1e18)
    for i in range(1, n + 1):
        for h in range(0, n + 1):
            if h != i:
                S[h, i] = W[arc[i][h]].sum()
    return S


def _eval(avg, dev, dv_arc):
    corr = tot = 0
    for si, s in enumerate(dev):
        n = len(s)
        head = mst_cle(_score_mat(avg, dv_arc[si], n))
        for i in range(1, n + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > n:
                continue
            corr += int(head.get(i, -1) == gh)
            tot += 1
    return corr / tot if tot else 0.0, corr, tot


def train_mst_retrain(train, dev, epochs, patience, seed):
    """Structured perceptron with MST inference; averaged weights; dev early-stop (best-epoch persisted)."""
    tr_arc = _precompute(train)
    dv_arc = _precompute(dev)
    rng = np.random.default_rng(seed)
    W = np.zeros(SIZE)
    CW = np.zeros(SIZE)
    c = 1
    best_uas = -1.0
    best_avg = None
    best_ep = 0
    history = []
    no_improve = 0
    for ep in range(epochs):
        te = time.time()
        for si in rng.permutation(len(train)):
            s = train[si]
            arc = tr_arc[si]
            n = len(s)
            pred = mst_cle(_score_mat(W, arc, n))
            for i in range(1, n + 1):
                gh = s[i - 1][3]
                if gh < 0 or gh > n:
                    continue
                ph = pred.get(i, -1)
                if ph != gh:
                    np.add.at(W, arc[i][gh], 1.0)
                    np.add.at(CW, arc[i][gh], c)
                    np.add.at(W, arc[i][ph], -1.0)
                    np.add.at(CW, arc[i][ph], -c)
            c += 1
        avg = W - CW / c
        uas, corr, tot = _eval(avg, dev, dv_arc)
        history.append({"epoch": ep + 1, "uas": round(uas, 4), "corr": corr, "tot": tot})
        print("[%s] ep %d MST-retrain dev UAS=%.4f (%d/%d) ep_time=%.1fs"
              % (ANCHOR_NAME, ep + 1, uas, corr, tot, time.time() - te), flush=True)
        if uas > best_uas:
            best_uas = uas
            best_avg = avg.copy()
            best_ep = ep + 1
            no_improve = 0
            CKPT_DIR.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(CKPT_DIR / "s1b_best_avg.npz", avg=best_avg.astype(np.float32),
                                epoch=best_ep, uas=best_uas)
        else:
            no_improve += 1
            if no_improve >= patience:
                print("[%s] early-stop at ep %d (best ep %d, uas %.4f)"
                      % (ANCHOR_NAME, ep + 1, best_ep, best_uas), flush=True)
                break
    return best_avg, best_uas, best_ep, history


# ================================================================================================
def _cfg(smoke):
    if smoke:
        return {"n_train": 400, "epochs": 3, "patience": 3, "maxlen": 50}
    return {"n_train": None, "epochs": 14, "patience": 3, "maxlen": 50}


def self_test():
    print("=== %s self-test (real code paths) ===" % ANCHOR_NAME, flush=True)
    # (1) CLE toy: rooted arborescence, no cycle.
    S = np.array([[0, 10, 3, 3], [0, 0, 20, 3], [0, 5, 0, 20], [0, 3, 5, 0]], dtype=float)
    h = mst_cle(S)
    assert set(h.keys()) == {1, 2, 3}, h
    for d in (1, 2, 3):
        x = d
        steps = 0
        while x != 0 and steps < 10:
            x = h[x]
            steps += 1
        assert x == 0, ("not rooted", d, h)
    # (2) MstArcParser round-trips the ArcParser interface + margins present.
    avg = ArcParser.load(str(CANON_ARC)).avg
    mp = MstArcParser(avg)
    r = mp.parse(["The", "cat", "sat", "."], ["DET", "NOUN", "VERB", "PUNCT"])
    assert len(r.arcs) == 4 and set(r.margins.keys()) == {1, 2, 3, 4}, r
    assert all(isinstance(v, float) for v in r.margins.values())
    # (3) save/load round-trip.
    import tempfile
    tf = os.path.join(tempfile.gettempdir(), "_mst_selftest.npz")
    mp.save(tf)
    mp2 = MstArcParser.load(tf)
    assert np.allclose(mp2.parse(["a", "b"], ["NOUN", "VERB"]).heads.get(1, -9),
                       mp.parse(["a", "b"], ["NOUN", "VERB"]).heads.get(1, -9))
    os.remove(tf)
    print("[selftest] PASS: CLE + MstArcParser interface + margins + save/load", flush=True)
    return True


def run(smoke: bool):
    t0 = time.time()
    cfg = _cfg(smoke)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train = [s for s in load_conllu("train") if 1 <= len(s) <= cfg["maxlen"]]
    dev = [s for s in load_conllu("dev") if 1 <= len(s) <= cfg["maxlen"]]
    if cfg["n_train"]:
        train = train[:cfg["n_train"]]
    print("[%s] train=%d dev=%d smoke=%s" % (ANCHOR_NAME, len(train), len(dev), smoke), flush=True)

    # S0: re-derive the REAL baseline (greedy decode on the persisted weights).
    s0_parser = ArcParser.load(str(CANON_ARC))
    s0_uas, s0_c, s0_t = s0_parser.eval_uas(dev)
    print("[%s] S0 greedy 1st-order dev UAS=%.4f (%d/%d)" % (ANCHOR_NAME, s0_uas, s0_c, s0_t), flush=True)

    # S1a: MST-inference on the SAME S0 weights (decode-only swap).
    s1a = MstArcParser(s0_parser.avg)
    s1a_uas, s1a_c, s1a_t = s1a.eval_uas(dev)
    print("[%s] S1a MST-inference dev UAS=%.4f (%d/%d)" % (ANCHOR_NAME, s1a_uas, s1a_c, s1a_t), flush=True)

    # S1b: MST-in-the-loop structured perceptron retrain, dev early-stop.
    best_avg, s1b_uas, s1b_ep, hist = train_mst_retrain(train, dev, cfg["epochs"], cfg["patience"], seed=1027)

    # Persist the BEST parser (S1b if it beats S1a, else S1a weights).
    if s1b_uas >= s1a_uas:
        persisted_uas = s1b_uas
        persisted_which = "S1b_mst_retrain"
        MstArcParser(best_avg).save(str(MST_ARC))
    else:
        persisted_uas = s1a_uas
        persisted_which = "S1a_mst_inference"
        MstArcParser(s0_parser.avg).save(str(MST_ARC))
    print("[%s] persisted %s UAS=%.4f -> %s" % (ANCHOR_NAME, persisted_which, persisted_uas, MST_ARC), flush=True)

    best_ladder = max(s1a_uas, s1b_uas)
    if best_ladder >= BASELINE_UAS + 0.005:
        verdict = "UAS_LIFT_REAL"
    elif best_ladder >= BASELINE_UAS - 0.003:
        verdict = "UAS_FLAT_PLATEAU"
    else:
        verdict = "UAS_REGRESS"

    msg = ("%s | S0_greedy=%.4f S1a_mst_inf=%.4f S1b_mst_retrain=%.4f(ep%d) | best_ladder=%.4f "
           "(delta_vs_baseline=%+.4f) | persisted=%s@%s" %
           (verdict, s0_uas, s1a_uas, s1b_uas, s1b_ep, best_ladder, best_ladder - s0_uas,
            persisted_which, MST_ARC.name))
    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": ("smoke" if smoke else "full"),
        "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(time.time() - t0, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_train": len(train), "n_dev": len(dev),
        "S0_greedy_1storder_uas": round(s0_uas, 4),
        "S1a_mst_inference_uas": round(s1a_uas, 4),
        "S1b_mst_retrain_uas": round(s1b_uas, 4), "S1b_best_epoch": s1b_ep,
        "best_ladder_uas": round(best_ladder, 4),
        "delta_vs_baseline": round(best_ladder - s0_uas, 4),
        "baseline_reref_uas": round(s0_uas, 4),
        "persisted_parser_path": str(MST_ARC), "persisted_which": persisted_which,
        "persisted_uas": round(persisted_uas, 4),
        "s1b_history": hist,
        "prior_2ndorder_measured_hurt": {"uas": 0.7783, "source": "data/exp_depparse_2ndorder_cpu_v1/metrics.json"},
        "compute_architecture": "sequential-CPU (justified)", "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True, "progress_logging": "print_flush_true",
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
        import traceback
        with open(OUT_DIR / "metrics.json.tmp", "w", encoding="utf-8") as f:
            json.dump({"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                       "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:400]),
                       "summary": "CELL_CRASHED", "elapsed_s": 0.0,
                       "traceback": traceback.format_exc()[:5000]}, f, indent=2)
        os.replace(OUT_DIR / "metrics.json.tmp", OUT_DIR / "metrics.json")
        raise
