"""exp_meaning_asset_ctx_readout_variants_v1 -- guard against "you tested a weak read-out".

The _CTX type vector in exp_meaning_asset_fair_test_v1 is the plain mean of a word's contextual
token reps. The standard practice for turning a contextual encoder into type vectors also removes
the dominant common direction (mean-centering; Mu & Viswanath 2018 "all-but-the-top"). If the
asset's meaning signal is being masked by a common component, the plain mean UNDERSTATES it and
the fair test would be testing a weak read-out.

This cell measures that, on the SAME high-power pair set and against the SAME hardened floor:
  RAW        the mean of the word's contextual token reps (what the fair test scored)
  CENTRED    RAW minus the mean over the whole vocabulary
  ABTT1/2    RAW minus its projection on the top 1 / top 2 principal directions
A random-init twin gets every variant too, so a gain that is really just "centering helps any
high-dimensional code" is visible.

SCOPE: the item population is SimLex+WordSim, not the instrument's vocabulary. NOT an instrument
number. This cell answers "is the read-out weak", not "does the asset clear the floor".

ASCII-only. CPU. No network. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS
import exp_meaning_asset_fair_test_v1 as FT
import exp_meaning_asset_power_extension_v1 as PX
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "meaning_asset_ctx_readout_variants_v1"
K_CTX = 8
SEED = 7
N_BOOT = 10000


def variants(X: np.ndarray) -> dict:
    out = {"RAW": INS._l2n(X)}
    C = X - X.mean(axis=0, keepdims=True)
    out["CENTRED"] = INS._l2n(C)
    U, S, Vt = np.linalg.svd(C, full_matrices=False)
    for k in (1, 2):
        P = Vt[:k]
        out[f"ABTT{k}"] = INS._l2n(C - (C @ P.T) @ P)
    return out


def main() -> int:
    t0 = time.time()
    simlex = INS.load_simlex(INS.SIMLEX)
    wordsim = PX.load_wordsim(PX.WORDSIM)
    from hdlab import grounded_similarity as GS
    norms = GS._table()
    vocab = sorted({w for a, b, _ in simlex + wordsim for w in (a, b)})
    w2i = {w: i for i, w in enumerate(vocab)}
    counts = PX.corpus_counts(vocab)
    occ, occ_stats = FT.build_occurrences(vocab, K_CTX)
    print(f"[vocab] {len(vocab)} [occ] {occ_stats['n_occurrences']}", flush=True)

    raw = {}
    for src, ck, ri in (("ASSET_V2", FT.CKPT_V2, False), ("CTRL_RANDINIT", FT.CKPT_V2, True)):
        enc = FT.TinyEnc(ck, random_init=ri, init_seed=7)
        X, st = enc.contextual_type(vocab, occ, tag=":" + src)
        raw[src] = X
        print(f"[ctx:{src}] {st}", flush=True)
    ortho = INS.enc_orthographic(vocab, 512, SEED)
    lf = np.log(counts + 1.0)

    results = {}
    for gold_name, prs in (("SIMLEX999", simlex), ("WORDSIM353", wordsim)):
        ps = [(a, b, s) for a, b, s in prs if a in w2i and b in w2i and a in norms and b in norms]
        gold = np.array([s for _, _, s in ps])
        la = np.array([lf[w2i[a]] for a, _, _ in ps])
        lb = np.array([lf[w2i[b]] for _, b, _ in ps])
        fch = {"FREQ_NEG_ABS_DIFF": -np.abs(la - lb), "FREQ_SUM": la + lb,
               "FREQ_MIN": np.minimum(la, lb)}
        frho = {k: FT._spearman(v, gold) for k, v in fch.items()}
        bfreq = max(frho, key=lambda k: frho[k])
        oc = np.array([float(ortho[w2i[a]] @ ortho[w2i[b]]) for a, b, _ in ps])
        floor_cands = {"HARDENED_FREQUENCY_" + bfreq: fch[bfreq], "A_ORTHOGRAPHIC": oc}
        rf = {k: FT._spearman(v, gold) for k, v in floor_cands.items()}
        bf = max(rf, key=lambda k: rf[k])
        block = {"n_pairs": len(ps), "floor_rho_by_arm": {k: round(v, 4) for k, v in rf.items()},
                 "strongest_floor": bf, "arms": {}}
        for src, X in raw.items():
            for vname, V in variants(X).items():
                c = np.array([float(V[w2i[a]] @ V[w2i[b]]) for a, b, _ in ps])
                d = FT.boot_rho_diff(c, floor_cands[bf], gold, n_boot=N_BOOT)
                block["arms"][f"{src}_CTX_{vname}"] = {
                    "rho": FT.boot_rho(c, gold, n_boot=N_BOOT),
                    "margin_over_strongest_floor": d, "band": FT.band(d["ci95"]),
                    "clears_floor": bool(FT.band(d["ci95"]) == "ABOVE"
                                         and d["point"] >= FT.T_MARGIN_MIN)}
        results[gold_name] = block
        print(f"[{gold_name}] n={len(ps)} floor={bf}({rf[bf]:.3f}) " +
              " ".join(f"{k.replace('_CTX_','.')}={v['rho']['point']:.3f}"
                       for k, v in block["arms"].items()), flush=True)

    clears = sorted({f"{g}|{a}" for g, b in results.items() for a, e in b["arms"].items()
                     if e["clears_floor"] and a.startswith("ASSET_")})
    out = {"anchor_name": ANCHOR_NAME, "run_mode": "full",
           "scope_disclaimer": ("item population is SimLex+WordSim, NOT the instrument's "
                                "vocabulary; this cell answers 'is the read-out weak', not "
                                "'does the asset clear the floor' on the instrument"),
           "verdict": ("A_STRONGER_READOUT_CLEARS_THE_FLOOR" if clears
                       else "NO_READOUT_VARIANT_CLEARS_THE_FLOOR"),
           "arms_clearing": clears, "occurrence_index": occ_stats, "results": results,
           "elapsed_s": round(time.time() - t0, 1)}
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_metrics(out_dir, out)
    print("VERDICT:", out["verdict"], clears, flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:                                          # noqa: BLE001 -- printed, not hidden
        import traceback
        traceback.print_exc()
        sys.exit(2)
