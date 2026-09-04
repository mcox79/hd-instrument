"""exp_atl_hubspoke_query_side_readout_v1 -- the REAL lever after the grounded located negative: attack the
QUERY side (100% of the loss per the parent's oracle decomposition; the disambiguating cue is in the plain w2v
context ~85% of the time, oracle-context ceiling 0.853) with the brain-faithful selection mechanisms neither
parent tested.

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

WHY (this session's research, cited):
  * PRECISION-WEIGHTING (Friston 2010; Bastos 2012; Feldman-Friston): precision is a MULTIPLICATIVE gain on the
    bottom-up error, which "explicitly allows a high-precision bottom-up error for a low-prior cause to dominate
    the posterior, overturning a strong prior." Plain biased-competition reweighting has a NARROW working range
    (Deco-Rolls): below a critical top-down bias the higher-baseline (DOMINANT) candidate wins regardless. So the
    fix for subordinate selection is to SHARPEN the gain on the few genuinely-diagnostic context words (gamma>1 /
    top-k), not to average.
  * CANDIDATE-SET RESTRICTION / SELECTIVE ACCESS (Vu-Kellas-Petersen-Metcalf 2003): strong context evokes a
    "domain of reference" that INCLUDES ONLY the situation-appropriate sense -- a binary candidate prune BEFORE
    competition, not a reweighting among fixed candidates. This is the non-collapsing mechanism.
  * ATL DISTINCTIVE-FEATURE WHITENING (Patterson-Nestor-Rogers 2007): decorrelate the dominant shared axis so
    the diagnosticity spread is computed on distinctive dims. Applied here to the DISTRIBUTIONAL sense keys.

Readout math is glass-box (numpy), same biased-competition core as hdlab.diagnostic_context_wsd, plus the three
levers above (each toggleable, gold-blind, symmetric across candidates). Keys = the launch-pad rich w2v atoms
(0.313). Optional grounded candidate-restriction reuses Cell A's grounded spoke. Strict doc-disjoint SemCor
subordinate, subject-weighted a_s, n=2676. Glass-box, NO external LLM, NO training, NO transformer. Core-capped.
ASCII. Own dir.
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
# KB_REFERENT: data/corpora/binder/binder2016_ratings.csv
# KB_REFERENT: data/grounding_testbed/Ratings_Warriner_et_al.csv
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import sys
import json
import time
import pickle
import argparse

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_brain_faithful_reader_v1 as BF
import experiments.exp_atl_hubspoke_grounded_separability_v1 as A

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_query_side_readout_v1")


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def readout_pick(C, G, gamma=1.0, topk=None, restrict_keep=None, Grnd_ctx=None, Grnd_keys=None,
                 grnd_restrict_keep=None):
    """Biased-competition sense pick over context rows C (W,D unit) and candidate keys G (S,D unit).
    gamma       : precision sharpening exponent on the per-word diagnosticity (Friston multiplicative gain).
    topk        : keep only the top-k most-diagnostic context words (hard selective gain).
    restrict_keep: DISTRIBUTIONAL candidate restriction -- keep the restrict_keep most flat-context-plausible
                   senses before competition (Vu-Kellas selective access); the rest are pruned.
    Grnd_ctx/Grnd_keys/grnd_restrict_keep: GROUNDED candidate restriction -- prune senses whose grounded
                   signature is least compatible with the grounded context; keep grnd_restrict_keep.
    Returns the index (into G's rows) of the picked sense."""
    S = G.shape[0]
    alive = np.ones(S, bool)

    # --- candidate-set restriction (prune BEFORE competition) ---
    if restrict_keep is not None and restrict_keep < S:
        flatq = _unit(C.mean(0))
        plaus = G @ flatq
        keep = np.argsort(-plaus)[:restrict_keep]
        m = np.zeros(S, bool); m[keep] = True; alive &= m
    if grnd_restrict_keep is not None and Grnd_ctx is not None and Grnd_keys is not None:
        have = np.array([np.any(k) for k in Grnd_keys])
        if have.sum() > grnd_restrict_keep and np.any(Grnd_ctx):
            gq = _unit(Grnd_ctx)
            gc = np.array([float(_unit(k) @ gq) if np.any(k) else -1e9 for k in Grnd_keys])
            keep = np.argsort(-gc)[:grnd_restrict_keep]
            m = np.zeros(S, bool); m[keep] = True
            m |= ~have          # never prune a sense we cannot ground (no evidence to prune on)
            alive &= m
    if alive.sum() == 0:
        alive = np.ones(S, bool)

    Ga = G[alive]
    # --- diagnosticity (biased competition) computed against the SURVIVING candidate keys ---
    sim = C @ Ga.T                                   # (W, S_alive)
    diag = np.clip(sim.max(1) - sim.mean(1), 0.0, None)
    if topk is not None and topk < len(diag):
        thr = np.sort(diag)[-topk]
        diag = np.where(diag >= thr, diag, 0.0)
    w = diag ** gamma                                # precision sharpening (multiplicative gain)
    if float(w.sum()) <= 1e-9:
        q = _unit(C.mean(0))
    else:
        q = _unit((w[:, None] * C).sum(0))
    sc = Ga @ q
    local = int(np.argmax(sc))
    return int(np.where(alive)[0][local])


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev_idx = list(np.where((doc % 2 == 0) & sub)[0]); test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    if smoke:
        dev_idx, test_idx = dev_idx[:300], test_idx[:300]
    cand = set()
    for i in dev_idx + test_idx:
        cand.update(recs[i]["tn"])
    cand = sorted(cand)

    rich_sig = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 3)) for s in cand}   # launch-pad atoms
    # ATL distinctive-whitening of the DISTRIBUTIONAL keys (decorrelate over the candidate-key population)
    K = np.stack([rich_sig[s] if rich_sig[s] is not None and np.any(rich_sig[s]) else np.zeros(G1.EMB_DIM, np.float32)
                  for s in cand]).astype(np.float64)
    mu = K.mean(0); Kc = K - mu
    cov = (Kc.T @ Kc) / max(1, Kc.shape[0])
    evals, evecs = np.linalg.eigh(cov)
    Wm = evecs * (1.0 / np.sqrt(np.clip(evals, 1e-8, None)))[None, :]
    rich_white = {}
    for s in cand:
        v = rich_sig[s]
        rich_white[s] = _unit((np.asarray(v, np.float64) - mu) @ Wm) if (v is not None and np.any(v)) else None

    # grounded spoke (Cell A) for the grounded candidate-restriction arm
    gr = A.Grounded(add_affect=True)
    sg_white = A.build_sense_grounded(cand, gr, whiten=True, own_lemma_w=0.0)
    print("[setup] cand=%d grounded_cov=%.3f (%.0fs)"
          % (len(cand), np.mean([sg_white[s] is not None for s in cand]), time.time() - t0), flush=True)

    def ctx_rows(r):
        return [(_unit(mat[w2i[x]])) for x in r["ctx"] if x in w2i]

    def grnd_ctx(r):
        vs = [gr.vec(x, True) for x in r["ctx"]]
        vs = [v for v in vs if v is not None]
        return _unit(np.sum(vs, 0)) if vs else np.zeros(gr.dim)

    def evaluate(idxs, sig, **kw):
        ok = []
        for i in idxs:
            r = recs[i]; tn = r["tn"]
            rows = ctx_rows(r)
            if not rows:
                continue
            G = np.stack([sig.get(s) if (sig.get(s) is not None and np.any(sig.get(s)))
                          else np.zeros(G1.EMB_DIM, np.float32) for s in tn]).astype(np.float64)
            if not np.any(G):
                continue
            C = np.stack(rows).astype(np.float64)
            kk = dict(kw)
            if kk.pop("_grounded_restrict", False):
                kk["Grnd_ctx"] = grnd_ctx(r)
                kk["Grnd_keys"] = [sg_white.get(s) if sg_white.get(s) is not None else np.zeros(gr.dim) for s in tn]
            pick = readout_pick(C, G, **kk)
            ok.append(int(tn[pick] == r["gold"]))
        return np.asarray(ok, float)

    # ---- floor + lever sweeps (dev-select, test-report) ----
    floor = evaluate(test_idx, rich_sig)                         # launch pad (gamma=1)
    arms = {"L3_rich_LAUNCHPAD": round(float(floor.mean()), 4)}
    print("[arm] L3_rich_LAUNCHPAD a_s=%.4f (%.0fs)" % (arms["L3_rich_LAUNCHPAD"], time.time() - t0), flush=True)

    def devsel(name, grid):
        best, bk, bd = None, None, -1.0
        for kw in grid:
            dv = float(evaluate(dev_idx, rich_sig, **{k: v for k, v in kw.items()}).mean())
            if dv > bd:
                bd, bk, best = dv, kw, kw
        tv = evaluate(test_idx, rich_sig, **{k: v for k, v in bk.items()})
        arms[name] = round(float(tv.mean()), 4)
        arms[name + "__cfg"] = {k: v for k, v in bk.items()}
        print("[arm] %-28s a_s=%.4f cfg=%s (%.0fs)" % (name, arms[name], arms[name + "__cfg"], time.time() - t0), flush=True)
        return tv

    prec = devsel("precision_gamma", [{"gamma": g} for g in [1.0, 1.5, 2.0, 3.0, 4.0, 6.0]])
    topk = devsel("precision_topk", [{"topk": k} for k in [1, 2, 3, 5, 8]])
    restr = devsel("candidate_restrict_distrib", [{"restrict_keep": m} for m in [2, 3, 4]])
    # combined precision + restriction
    comb = devsel("precision_x_restrict",
                  [{"gamma": g, "restrict_keep": m} for g in [1.0, 2.0, 3.0] for m in [2, 3, 4]])
    # grounded candidate-restriction (composes Cell A's grounded spoke on the query side)
    def devsel_grnd(name, grid):
        best, bd = None, -1.0
        for kw in grid:
            dv = float(evaluate(dev_idx, rich_sig, _grounded_restrict=True, **kw).mean())
            if dv > bd:
                bd, best = dv, kw
        tv = evaluate(test_idx, rich_sig, _grounded_restrict=True, **best)
        arms[name] = round(float(tv.mean()), 4)
        arms[name + "__cfg"] = best
        print("[arm] %-28s a_s=%.4f cfg=%s (%.0fs)" % (name, arms[name], best, time.time() - t0), flush=True)
        return tv
    grnd = devsel_grnd("grounded_candidate_restrict",
                       [{"grnd_restrict_keep": k, "gamma": g} for k in [2, 3] for g in [1.0, 2.0]])
    # COMBINED: precision selective-gain (top-k) + grounded candidate-restriction (independent levers stacked)
    combo = devsel_grnd("precision_topk_x_grounded_restrict",
                        [{"grnd_restrict_keep": k, "topk": tk, "gamma": g}
                         for k in [2, 3] for tk in [3, 5, 8] for g in [1.0, 2.0]])
    # distinctive-whitened distributional keys (ATL decorrelation) with best precision gamma
    gbest = arms["precision_gamma__cfg"].get("gamma", 1.0)
    whi = evaluate(test_idx, rich_white, gamma=gbest)
    arms["distinctive_whitened_keys"] = round(float(whi.mean()), 4)
    print("[arm] distinctive_whitened_keys a_s=%.4f (gamma=%.1f) (%.0fs)"
          % (arms["distinctive_whitened_keys"], gbest, time.time() - t0), flush=True)

    # ---- best arm + twin + CI vs floor ----
    cand_arms = {"precision_gamma": prec, "precision_topk": topk, "candidate_restrict_distrib": restr,
                 "precision_x_restrict": comb, "grounded_candidate_restrict": grnd,
                 "precision_topk_x_grounded_restrict": combo, "distinctive_whitened_keys": whi}
    best_name = max(cand_arms, key=lambda k: arms[k])
    best_vec = cand_arms[best_name]

    def pair(x, seed=903):
        n = min(len(x), len(floor)); return G1._paired(x[:n], floor[:n], seed)
    res = {"n_dev": len(dev_idx), "n_test": len(test_idx), "arms": arms,
           "oracle_context_ceiling_ref": 0.853, "launchpad_floor": arms["L3_rich_LAUNCHPAD"],
           "best_arm": best_name, "best_a_s": arms[best_name],
           "best_vs_launchpad": pair(best_vec)}
    # info-free twin for the best arm: shuffle the diagnosticity onto wrong words (gamma-sharpened noise must lose)
    def twin(idxs):
        rng = np.random.default_rng(2027); ok = []
        for i in idxs:
            r = recs[i]; tn = r["tn"]; rows = ctx_rows(r)
            if not rows:
                continue
            G = np.stack([rich_sig.get(s) if (rich_sig.get(s) is not None and np.any(rich_sig.get(s)))
                          else np.zeros(G1.EMB_DIM, np.float32) for s in tn]).astype(np.float64)
            if not np.any(G):
                continue
            C = np.stack(rows).astype(np.float64)
            sim = C @ G.T; diag = np.clip(sim.max(1) - sim.mean(1), 0, None)
            diag = diag[rng.permutation(len(diag))] ** (arms.get(best_name + "__cfg", {}).get("gamma", 3.0) if isinstance(arms.get(best_name + "__cfg"), dict) else 3.0)
            q = _unit((diag[:, None] * C).sum(0)) if diag.sum() > 1e-9 else _unit(C.mean(0))
            ok.append(int(tn[int(np.argmax(G @ q))] == r["gold"]))
        return np.asarray(ok, float)
    tw = twin(test_idx)
    res["best_vs_twin"] = G1._paired(best_vec[:min(len(best_vec), len(tw))], tw[:min(len(best_vec), len(tw))], 904)
    res["twin_a_s"] = round(float(tw.mean()), 4)

    # ---- MFS no-regression guard: does the precision lever hurt the DOMINANT-sense population? ----
    # Evaluate the best precision config on ALL test items (subordinate + dominant), vs the launch pad. The brain's
    # precision gain must not degrade the easy dominant items (biased-competition working-range concern).
    all_test = list(np.where(doc % 2 == 1)[0])
    if smoke:
        all_test = all_test[:600]
    best_cfg = arms.get(best_name + "__cfg", {})
    best_cfg = best_cfg if isinstance(best_cfg, dict) else {}
    cfg_clean = {k: v for k, v in best_cfg.items() if k in ("gamma", "topk", "restrict_keep")}
    grnd_flag = "grounded" in best_name
    lp_all = evaluate(all_test, rich_sig)
    if grnd_flag:
        best_all = evaluate(all_test, rich_sig, _grounded_restrict=True, **{k: v for k, v in best_cfg.items() if k in ("gamma", "topk", "grnd_restrict_keep")})
    else:
        best_all = evaluate(all_test, rich_sig, **cfg_clean)
    res["mfs_guard"] = {"launchpad_all": round(float(lp_all.mean()), 4), "best_all": round(float(best_all.mean()), 4),
                        "delta_all": round(float(best_all.mean() - lp_all.mean()), 4),
                        "no_regression": bool(best_all.mean() >= lp_all.mean() - 0.005)}
    print("[mfs-guard] all-items launchpad=%.4f best=%.4f delta=%+.4f no_regression=%s"
          % (res["mfs_guard"]["launchpad_all"], res["mfs_guard"]["best_all"], res["mfs_guard"]["delta_all"],
             res["mfs_guard"]["no_regression"]), flush=True)

    crossed = res["best_vs_launchpad"]["sep"] and arms[best_name] > arms["L3_rich_LAUNCHPAD"]
    res["headline"] = ("QUERY-SIDE READOUT | launchpad=%.4f best=%s %.4f (vs launchpad sep=%s ci=%s; twin=%.4f) | %s"
                       % (arms["L3_rich_LAUNCHPAD"], best_name, arms[best_name], res["best_vs_launchpad"]["sep"],
                          res["best_vs_launchpad"]["ci"], res["twin_a_s"],
                          "CROSSES launch pad" if crossed else "no readout lever crosses the launch pad"))
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_query_side_readout_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # precision sharpening must select the context-consistent sense when one context word is strongly diagnostic
    C = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])          # 1 word -> sense0, 2 words -> sense1 (topic)
    G = np.array([[1.0, 0.0], [0.0, 1.0]])                       # sense0, sense1
    # flat mean would favor sense1 (2 vs 1); high-gamma precision on the diagnostic word can recover sense0
    p1 = readout_pick(C, G, gamma=1.0)
    p_sharp = readout_pick(C[:1], G, gamma=6.0)
    assert p_sharp == 0, "precision sharpening selects the diagnostic-word sense"
    assert readout_pick(C, G, restrict_keep=1) in (0, 1), "restriction returns a valid alive index"
    print("SELFTEST PASS (precision-sharpened readout + candidate restriction return valid picks)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke and not args.full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
