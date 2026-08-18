"""Parser UAS headroom leak-hunt: is ~0.80 UAS UNDER-TRAINED/UNDER-FEATURED or SATURATED?

Amends atom 29402 ("classical nearly-tapped ~0.80"). 29402 tested MST-decode + char/POS/shape
features at 5-6 epochs and read 0.7965 (MST) / 0.7925 (rich). It did NOT test the two dimensions
the lit uses to reach 0.86-0.89 UAS on UD-EWT: (a) the LEARNING CURVE (epochs + data size), and
(b) fuller POS-GRANULARITY features. This harness probes both, plus two CHEAP gap-explainer leaks
found by inspection.

PRIOR-WORK CHECK (substrate_query.sh "dependency parser UAS learning curve feature templates
structured perceptron arc-eager"): top hits COLLINS_STRUCTURED_PERCEPTRON_TEST cosine=0.34 and the
June drill research_drill_dep_parse_0787_to_085 cosine=0.31. This is a direct CONTINUATION/AMENDMENT
of that arc (atom 29402), NOT a rediscovery. CITED@notes/research_drill_dep_parse_0787_to_085 2026-06-11.

TWO LEAK-HUNT HYPOTHESES found by inspecting the substrate (both CHEAP + decisive):
  L1 POS-GRANULARITY: hdlab/arc_parser + _ud_loader read UPOS (17 coarse tags, c[3]). The lit's
     feature-engineered parsers (McDonald 2005, Zhang-Nivre 2011) use FINE-GRAINED POS (~45 PTB tags).
     UD-EWT carries XPOS (c[4]) FULLY POPULATED (49 distinct tags, 0 empty MEASURED). Coarse UPOS
     collapses tense/number/degree distinctions that are highly attachment-informative. Swapping the
     POS-column content (UPOS -> XPOS -> UPOS|XPOS combo) through the IDENTICAL _arc_ids feature fn is
     a clean ONE-VARIABLE representation test. This is NOT training/data -- it is representation.
  L2 PUNCT CONVENTION: our eval_uas counts ALL arcs incl punctuation dependents (12.3% of dev arcs
     MEASURED). Classic feature-engineered-parser UAS EXCLUDES punctuation. Punct attachment in UD is
     hard/arbitrary, so UAS-with-punct DEFLATES vs a UAS-excl-punct lit number. Free to measure.

PHASES (each phase's result persisted to ckpt/phase_<X>.json immediately; resumable):
  A  design-gate diagnostics : re-derive canon greedy (0.7868) + MST (0.7965) UAS, ALL and EXCL-PUNCT.
  B  epoch learning curve    : greedy 1st-order, full 12329 train, snapshot avg-weights at ep {5,10,20,40}.
                               (canon used 10 ep. Averaged perceptron sometimes needs 15-25. Saturated?)
  C  data-size curve         : greedy at fixed ep, train {3000, 6000, 12329}. Still rising with data?
  D  POS-granularity (L1)     : greedy, matched ep, POS-column {upos, xpos, combo}. -> toward 0.86-0.89?

DESIGN-GATE (pre-registered; verified inline):
  (1) REAL baseline = persisted canon greedy 0.7868 UAS + MST 0.7965, RE-DERIVED live on UD-EWT dev.
  (2) CAN-FAIL: (a) all curves saturate at ~0.80 despite more ep/data/fine-POS = 29402 CONFIRMED
      (hashed-perceptron setup caps below lit; a real representation/setup bound); (b) a lever climbs
      toward 0.86-0.89 = 29402 OVER-READ, classical headroom = autonomous reader lift. Both reportable.
  (3) DIFFICULTY-ON = held-out UD-EWT dev (1989 sents / 24444 arcs), same eval as the persisted parser.
  (4) ONE-VARIABLE per phase: B=epochs, C=train-size, D=POS-column-content (features fn IDENTICAL).

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified: pure-python hashed avg-perceptron; UD-EWT
  avg len ~16; canon full-train x 10ep MEASURED ~180s). storage: no_storage (persists nothing to the
  substrate; writes only diagnostic metrics). progress_logging: print_flush_true (long cell). determinism:
  FIXED int seed, numpy default_rng, sorted/enumerated iteration; NO hash()-seeded RNG, NO list(set()).
  LOCAL-ONLY foreground-to-completion; NO queue, NO push, NO remote-persist, NO substrate store write,
  NO git add. Resumable: each phase checkpointed; --resume skips phases whose ckpt exists.

CELL-TEMPLATE: except SystemExit: raise BEFORE except Exception (no BaseException); atomic tmp_replace
  metrics; all numbers tagged MEASURED@/CITED@/THEORETICAL@. arms_differ verified via distinct POS-column.

NO LLM. NO nltk. NO torch. numpy + pure-python only. ASCII-only.
"""
from __future__ import annotations

import argparse
import json
import os
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

from hdlab.arc_parser import _arc_ids, _decode, SIZE, ArcParser  # noqa: E402

ANCHOR_NAME = "parser_uas_headroom_leakhunt_v1"
UD_DIR = REPO / "experiments" / "data" / "ud_english_ewt"
FRONTEND_DIR = REPO / "data" / "frontend_assets"
CANON_ARC = FRONTEND_DIR / "arc_parser_hashed_ud_ewt.npz"            # S0 greedy 1st-order (0.7868)
MST_ARC = FRONTEND_DIR / "arc_parser_mst_retrain_ud_ewt.npz"        # S1b MST-retrain (0.7965)
OUT_DIR = REPO / "data" / f"exp_{ANCHOR_NAME}"
CKPT_DIR = OUT_DIR / "ckpt"

BASELINE_CANON_UAS = 0.7868   # MEASURED@data/exp_depparse_hashed_cpu_v1/metrics.json (10 ep, 12329 train)
BASELINE_MST_UAS = 0.7965     # MEASURED@data/exp_parser_uas_ladder_mst_retrain_v1/metrics.json
LIT_LOW, LIT_HIGH = 0.86, 0.89  # CITED@notes/research_drill_dep_parse_0787_to_085 (feat-eng UD-EWT)
SEED = 1027
MAXLEN = 50


# ================================================================================================
# Loading: POS-column content is the ONLY thing that varies across the D-arms.
#   upos  = c[3] (17 coarse)   xpos = c[4] (49 fine PTB)   combo = c[3]+"|"+c[4] (finest)
# We ALSO keep the UPOS of every token (for the punct-exclusion eval mask, arm-independent).
# ================================================================================================
def _load(split: str, pos_kind: str) -> Tuple[list, list]:
    """Returns (sents, upos_sents). sents use pos_kind in the POS field; upos_sents always UPOS (mask)."""
    fp = UD_DIR / ("en_ewt-ud-%s.conllu" % split)
    sents: list = []
    upos_sents: list = []
    cur: list = []
    cur_u: list = []
    with open(fp, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur); upos_sents.append(cur_u); cur = []; cur_u = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) < 8 or "-" in c[0] or "." in c[0]:
                continue
            try:
                idx = int(c[0]); head = int(c[6])
            except Exception:
                continue
            upos, xpos = c[3], c[4]
            if pos_kind == "upos":
                pf = upos
            elif pos_kind == "xpos":
                pf = xpos if xpos not in ("", "_") else upos
            elif pos_kind == "combo":
                pf = upos + "|" + (xpos if xpos not in ("", "_") else upos)
            else:
                raise ValueError("pos_kind %r" % pos_kind)
            cur.append((idx, c[1], pf, head, c[7]))
            cur_u.append((idx, c[1], upos, head, c[7]))
    if cur:
        sents.append(cur); upos_sents.append(cur_u)
    keep = [i for i, s in enumerate(sents) if 1 <= len(s) <= MAXLEN]
    return [sents[i] for i in keep], [upos_sents[i] for i in keep]


# ================================================================================================
# Training: verbatim arc-factored greedy avg-perceptron algorithm (hdlab.arc_parser.train_arc), but
# SNAPSHOTS averaged weights at requested epoch checkpoints so one run yields the whole epoch curve.
# ================================================================================================
def _precompute(sents: Sequence[Sequence[tuple]]) -> list:
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


def train_greedy_snapshots(train, checkpoints: List[int], max_ep: int, seed: int) -> Dict[int, np.ndarray]:
    """Greedy local-argmax avg-perceptron (verbatim). Returns {ep: averaged_weights} for ep in checkpoints."""
    rng = np.random.default_rng(seed)
    tr_arc = _precompute(train)
    W = np.zeros(SIZE)
    CW = np.zeros(SIZE)
    c = 1
    snaps: Dict[int, np.ndarray] = {}
    cps = set(checkpoints)
    for ep in range(max_ep):
        te = time.time()
        for si in rng.permutation(len(train)):
            s = train[si]
            arc = tr_arc[si]
            n = len(s)
            for i in range(1, n + 1):
                gold_h = s[i - 1][3]
                if gold_h < 0 or gold_h > n:
                    continue
                best_h = -1
                best_s = -1e18
                for h in range(0, n + 1):
                    if h == i:
                        continue
                    sc = W[arc[i][h]].sum()
                    if sc > best_s:
                        best_s = sc
                        best_h = h
                if best_h != gold_h:
                    np.add.at(W, arc[i][gold_h], 1.0)
                    np.add.at(CW, arc[i][gold_h], c)
                    np.add.at(W, arc[i][best_h], -1.0)
                    np.add.at(CW, arc[i][best_h], -c)
                c += 1
        if (ep + 1) in cps:
            snaps[ep + 1] = (W - CW / c).copy()
            print("[%s]   snapshot ep %d (ep_time~%.1fs, running)" % (ANCHOR_NAME, ep + 1, time.time() - te), flush=True)
    return snaps


# ================================================================================================
# Eval: greedy decode (verbatim _decode) -> UAS ALL arcs AND UAS excl-punct (dep UPOS==PUNCT dropped).
# ================================================================================================
def eval_both(avg: np.ndarray, dev, dev_upos, maxlen: int = MAXLEN) -> Dict[str, float]:
    corr_all = tot_all = corr_np = tot_np = 0
    for si, s in enumerate(dev):
        n = len(s)
        arc = [[None] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for h in range(0, n + 1):
                if h != i:
                    arc[i][h] = _arc_ids(s, i, h)
        head, _ = _decode(avg, arc, n)
        us = dev_upos[si]
        for i in range(1, n + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > n:
                continue
            ok = int(head.get(i, -1) == gh)
            corr_all += ok
            tot_all += 1
            if us[i - 1][2] != "PUNCT":
                corr_np += ok
                tot_np += 1
    return {
        "uas_all": round(corr_all / tot_all, 4) if tot_all else 0.0,
        "uas_nopunct": round(corr_np / tot_np, 4) if tot_np else 0.0,
        "n_arcs_all": tot_all, "n_arcs_nopunct": tot_np,
    }


def _write_ckpt(name: str, payload: dict) -> None:
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CKPT_DIR / (name + ".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, CKPT_DIR / (name + ".json"))


def _read_ckpt(name: str):
    p = CKPT_DIR / (name + ".json")
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None


# ================================================================================================
def _cfg(smoke: bool) -> dict:
    if smoke:
        return {"n_train_full": 300, "epoch_cps": [1, 2], "epoch_max": 2,
                "data_sizes": [150, 300], "data_ep": 2, "pos_ep": [2], "pos_max": 2}
    return {"n_train_full": None, "epoch_cps": [5, 10, 20, 40], "epoch_max": 40,
            "data_sizes": [3000, 6000, 12329], "data_ep": 20, "pos_ep": [10, 20], "pos_max": 20}


def self_test() -> bool:
    print("=== %s self-test (real code paths) ===" % ANCHOR_NAME, flush=True)
    # real loader on a tiny slice + real feature fn + real decode + real eval, all exercised.
    dev, dev_u = _load("dev", "upos")
    assert len(dev) > 100 and len(dev) == len(dev_u), (len(dev), len(dev_u))
    # xpos + combo arms load and DIFFER from upos in the POS column (arms-must-differ).
    dvx, _ = _load("dev", "xpos")
    dvc, _ = _load("dev", "combo")
    pos_u = dev[0][0][2]; pos_x = dvx[0][0][2]; pos_c = dvc[0][0][2]
    assert pos_u != pos_x, ("upos==xpos in POS column?", pos_u, pos_x)
    assert "|" in pos_c and pos_c.startswith(pos_u), ("combo malformed", pos_c)
    # real trained-weights eval reproduces canon within tolerance (positive control at tiny dev slice).
    avg = ArcParser.load(str(CANON_ARC)).avg
    r = eval_both(avg, dev[:50], dev_u[:50])
    assert 0.5 < r["uas_all"] <= 1.0, r
    assert r["uas_nopunct"] >= r["uas_all"] - 0.05, ("nopunct should not be far below all", r)
    # tiny snapshot train exercises the real perceptron loop.
    snaps = train_greedy_snapshots(dev[:60], [1], 1, SEED)
    assert 1 in snaps and snaps[1].shape == (SIZE,), snaps.keys()
    print("[selftest] PASS: loader(upos/xpos/combo differ) + eval_both(all+nopunct) + snapshot train", flush=True)
    return True


def run(smoke: bool, resume: bool) -> dict:
    t0 = time.time()
    cfg = _cfg(smoke)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CKPT_DIR.mkdir(parents=True, exist_ok=True)

    # dev is shared across all phases; upos mask is arm-independent.
    dev_u_sents, dev_u_mask = _load("dev", "upos")
    dev_x_sents, _ = _load("dev", "xpos")
    dev_c_sents, _ = _load("dev", "combo")
    print("[%s] dev=%d sents (upos/xpos/combo POS-columns loaded)" % (ANCHOR_NAME, len(dev_u_sents)), flush=True)

    # ---------- PHASE A: design-gate diagnostics (re-derive baselines, all + nopunct) ----------
    A = _read_ckpt("phase_A") if resume else None
    if A is None:
        print("[%s] PHASE A: re-derive canon greedy + MST baselines (all + excl-punct)..." % ANCHOR_NAME, flush=True)
        canon = ArcParser.load(str(CANON_ARC)).avg
        canon_ev = eval_both(canon, dev_u_sents, dev_u_mask)
        # NOTE: MST-retrain weights are optimized for CLE/MST global decode; evaluating them under the
        # GREEDY _decode here is APPLES-TO-ORANGES (the cited 0.7965 was measured with CLE). Kept only as
        # a cross-check that the greedy-decode number is lower (expected), NOT as "the MST parser UAS".
        mst_ev = None
        if MST_ARC.exists():
            mst = np.load(str(MST_ARC))["avg"].astype(np.float64)
            mst_ev = eval_both(mst, dev_u_sents, dev_u_mask)
        A = {"canon_greedy": canon_ev, "mst_retrain_under_GREEDY_decode_apples_to_oranges": mst_ev,
             "canon_cited": BASELINE_CANON_UAS, "mst_cited_CLE_decode": BASELINE_MST_UAS,
             "baseline_reproduces": abs(canon_ev["uas_all"] - BASELINE_CANON_UAS) <= 0.003}
        _write_ckpt("phase_A", A)
    _mstA = A.get("mst_retrain_under_GREEDY_decode_apples_to_oranges") or {}
    print("[%s] PHASE A done: canon all=%.4f nopunct=%.4f | mst(greedy-decode,apples-oranges) all=%s | reproduces=%s"
          % (ANCHOR_NAME, A["canon_greedy"]["uas_all"], A["canon_greedy"]["uas_nopunct"],
             _mstA.get("uas_all"), A["baseline_reproduces"]), flush=True)

    # ---------- PHASE B: epoch learning curve (greedy, full train) ----------
    B = _read_ckpt("phase_B") if resume else None
    if B is None:
        tr_u, _ = _load("train", "upos")
        if cfg["n_train_full"]:
            tr_u = tr_u[:cfg["n_train_full"]]
        print("[%s] PHASE B: epoch curve, greedy upos, train=%d, cps=%s..."
              % (ANCHOR_NAME, len(tr_u), cfg["epoch_cps"]), flush=True)
        snaps = train_greedy_snapshots(tr_u, cfg["epoch_cps"], cfg["epoch_max"], SEED)
        curve = {}
        for ep in sorted(snaps):
            curve[ep] = eval_both(snaps[ep], dev_u_sents, dev_u_mask)
            print("[%s]   ep %d -> UAS all=%.4f nopunct=%.4f"
                  % (ANCHOR_NAME, ep, curve[ep]["uas_all"], curve[ep]["uas_nopunct"]), flush=True)
        B = {"n_train": len(tr_u), "curve": {str(k): v for k, v in curve.items()}}
        _write_ckpt("phase_B", B)
    print("[%s] PHASE B done" % ANCHOR_NAME, flush=True)

    # ---------- PHASE C: data-size curve (greedy, fixed epochs) ----------
    C = _read_ckpt("phase_C") if resume else None
    if C is None:
        tr_full, _ = _load("train", "upos")
        print("[%s] PHASE C: data curve, greedy upos, ep=%d, sizes=%s..."
              % (ANCHOR_NAME, cfg["data_ep"], cfg["data_sizes"]), flush=True)
        dcurve = {}
        for nsz in cfg["data_sizes"]:
            sub = tr_full[:nsz]
            snaps = train_greedy_snapshots(sub, [cfg["data_ep"]], cfg["data_ep"], SEED)
            ev = eval_both(snaps[cfg["data_ep"]], dev_u_sents, dev_u_mask)
            dcurve[nsz] = ev
            print("[%s]   n_train=%d ep=%d -> UAS all=%.4f nopunct=%.4f"
                  % (ANCHOR_NAME, len(sub), cfg["data_ep"], ev["uas_all"], ev["uas_nopunct"]), flush=True)
        C = {"data_ep": cfg["data_ep"], "curve": {str(k): v for k, v in dcurve.items()}}
        _write_ckpt("phase_C", C)
    print("[%s] PHASE C done" % ANCHOR_NAME, flush=True)

    # ---------- PHASE D: POS-granularity (L1) upos vs xpos vs combo ----------
    D = _read_ckpt("phase_D") if resume else None
    if D is None:
        print("[%s] PHASE D: POS-granularity, ep=%s..." % (ANCHOR_NAME, cfg["pos_ep"]), flush=True)
        arms = {}
        dev_by_arm = {"upos": (dev_u_sents, dev_u_mask), "xpos": (dev_x_sents, dev_u_mask),
                      "combo": (dev_c_sents, dev_u_mask)}
        for arm in ("upos", "xpos", "combo"):
            tr_arm, _ = _load("train", arm)
            snaps = train_greedy_snapshots(tr_arm, cfg["pos_ep"], cfg["pos_max"], SEED)
            dv_s, dv_m = dev_by_arm[arm]
            arm_curve = {}
            for ep in sorted(snaps):
                arm_curve[ep] = eval_both(snaps[ep], dv_s, dv_m)
                print("[%s]   arm=%s ep=%d -> UAS all=%.4f nopunct=%.4f"
                      % (ANCHOR_NAME, arm, ep, arm_curve[ep]["uas_all"], arm_curve[ep]["uas_nopunct"]), flush=True)
            arms[arm] = {"n_train": len(tr_arm), "curve": {str(k): v for k, v in arm_curve.items()}}
        D = {"arms": arms, "note": "IDENTICAL _arc_ids feature fn; only POS-column content differs. "
             "between-VERB/PUNCT features (literal UPOS strings in _arc_ids) are inert for xpos/combo "
             "=> conservative for those arms."}
        _write_ckpt("phase_D", D)
    print("[%s] PHASE D done" % ANCHOR_NAME, flush=True)

    # ---------- VERDICT ----------
    canon_all = A["canon_greedy"]["uas_all"]
    # best across all learning/feature levers (uas_all convention, matched to baseline).
    ep_best = max(v["uas_all"] for v in B["curve"].values())
    data_best = max(v["uas_all"] for v in C["curve"].values())
    pos_best_arm, pos_best = None, -1.0
    for arm, d in D["arms"].items():
        for ep, v in d["curve"].items():
            if v["uas_all"] > pos_best:
                pos_best = v["uas_all"]; pos_best_arm = "%s@ep%s" % (arm, ep)
    overall_best = max(canon_all, ep_best, data_best, pos_best)
    lift = overall_best - canon_all

    # nopunct convention: the fairest comparison to lit numbers.
    pos_best_np = -1.0
    for arm, d in D["arms"].items():
        for ep, v in d["curve"].items():
            pos_best_np = max(pos_best_np, v["uas_nopunct"])
    canon_np = A["canon_greedy"]["uas_nopunct"]

    # Interpretation bands (best classical lever vs the LIT 0.86-0.89 target, uas_all convention).
    if overall_best >= 0.83:
        verdict = "UNDER_FEATURED_29402_OVERREAD"   # big classical headroom found
    elif overall_best >= canon_all + 0.02:
        verdict = "PARTIAL_HEADROOM"                 # meaningful but not lit-ceiling
    else:
        verdict = "SATURATED_29402_HOLDS"            # ~0.80 cap; needs better representation
    msg = ("%s | canon_all=%.4f (nopunct=%.4f) | epoch_best=%.4f data_best=%.4f pos_best=%.4f(%s) | "
           "overall_best=%.4f lift=%+.4f | pos_best_nopunct=%.4f canon_nopunct=%.4f | lit_target=%.2f-%.2f"
           % (verdict, canon_all, canon_np, ep_best, data_best, pos_best, pos_best_arm,
              overall_best, lift, pos_best_np, canon_np, LIT_LOW, LIT_HIGH))

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": ("smoke" if smoke else "full"),
        "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(time.time() - t0, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "phase_A_baselines": A, "phase_B_epoch_curve": B, "phase_C_data_curve": C, "phase_D_pos_granularity": D,
        "overall_best_uas_all": round(overall_best, 4), "lift_vs_canon": round(lift, 4),
        "pos_best_nopunct": round(pos_best_np, 4), "canon_nopunct": round(canon_np, 4),
        "lit_target": [LIT_LOW, LIT_HIGH],
        "canon_cited": BASELINE_CANON_UAS, "mst_cited": BASELINE_MST_UAS,
        "compute_architecture": "sequential-CPU (justified)", "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True, "progress_logging": "print_flush_true",
        "leak_hunt": {"L1_pos_granularity": "phase_D", "L2_punct_convention": "uas_nopunct fields"},
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
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(smoke=args.smoke, resume=args.resume)


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
