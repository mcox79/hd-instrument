"""exp_meaning_asset_power_extension_v2_paired -- the high-power readout, with PAIRED margins
against the HARDENED floor.

v1 of the power extension reports each arm's rho and a paired difference against its own
projected frequency floor, but does not persist the per-pair cosines, so its margins cannot be
recomputed against the STRONGER seed-free frequency channels found by
exp_meaning_asset_floor_hardening_v1. This cell redoes the same encoding work and persists the
per-pair cosines, so every margin is a PAIRED bootstrap against
max(A_ORTHOGRAPHIC, strongest seed-free FREQUENCY channel, that arm's own SCRAMBLE).

SAME SCOPE DISCLAIMER AS v1 OF THE EXTENSION: the item population is the SimLex-999 + WordSim-353
word list, NOT the instrument's frequency-ranked vocabulary. These are NOT instrument numbers.
Identity and bundling are not measured here. What is bought is POWER: ~3x the pairs.

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

ANCHOR_NAME = "meaning_asset_power_extension_v2_paired"
K_CTX = 8
SEED = 7
N_BOOT = 10000


def main() -> int:
    t0 = time.time()
    simlex = INS.load_simlex(INS.SIMLEX)
    wordsim = PX.load_wordsim(PX.WORDSIM)
    from hdlab import grounded_similarity as GS
    norms = GS._table()
    brys = FT.brysbaert_conc()

    vocab = sorted({w for a, b, _ in simlex + wordsim for w in (a, b)})
    w2i = {w: i for i, w in enumerate(vocab)}
    counts = PX.corpus_counts(vocab)
    occ, occ_stats = FT.build_occurrences(vocab, K_CTX)
    print(f"[vocab] {len(vocab)}  [occ] {occ_stats}", flush=True)

    codes = {}
    for src, ck, ri in (("V2", FT.CKPT_V2, False), ("RETRAIN", FT.CKPT_RETRAIN, False),
                        ("RANDINIT", FT.CKPT_V2, True)):
        enc = FT.TinyEnc(ck, random_init=ri, init_seed=7)
        pre = "CTRL_RANDINIT" if ri else f"ASSET_{src}"
        codes[pre + "_TOKEMB"] = enc.tokemb(vocab)
        codes[pre + "_ISOL"] = enc.isolated(vocab)
        X, st = enc.contextual_type(vocab, occ, tag=":" + src)
        codes[pre + "_CTX"] = X
        print(f"[ctx:{src}] {st}", flush=True)
    codes["ASSET_NORMS12"] = FT.enc_norms12(vocab, 12, SEED)
    codes["A_ORTHOGRAPHIC"] = INS.enc_orthographic(vocab, 512, SEED)
    codes["A_RANDOM_IID"] = INS.enc_random_iid(vocab, 512, SEED)
    codes["P_LIVE_WORD"] = INS.enc_live_word(vocab, 256, SEED)
    codes["CTRL_CONCRETENESS_ONLY"] = FT.enc_concreteness_only(vocab, 512, SEED)
    for a in [k for k in list(codes) if k.startswith("ASSET_")]:
        codes[a + "_SHUFFLED"] = codes[a][np.random.default_rng(SEED ^ 0xC0FFEE)
                                          .permutation(len(vocab))]

    lf = np.log(counts + 1.0)
    results = {}
    for gold_name, prs in (("SIMLEX999", simlex), ("WORDSIM353", wordsim)):
        ps = [(a, b, s) for a, b, s in prs if a in w2i and b in w2i and a in norms and b in norms]
        if len(ps) < 50:
            continue
        gold = np.array([s for _, _, s in ps])
        la = np.array([lf[w2i[a]] for a, _, _ in ps])
        lb = np.array([lf[w2i[b]] for _, b, _ in ps])
        fch = {"FREQ_NEG_ABS_DIFF": -np.abs(la - lb), "FREQ_SUM": la + lb,
               "FREQ_MIN": np.minimum(la, lb),
               "FREQ_MIN_OVER_MAX": np.minimum(la, lb) / np.maximum(np.maximum(la, lb), 1e-12)}
        frho = {k: FT._spearman(v, gold) for k, v in fch.items()}
        bfreq = max(frho, key=lambda k: frho[k])
        cos = {k: np.array([float(V[w2i[a]] @ V[w2i[b]]) for a, b, _ in ps])
               for k, V in codes.items()}
        ctrl = np.column_stack([
            np.array([0.5 * (brys.get(a, np.nan) + brys.get(b, np.nan)) for a, b, _ in ps]),
            np.array([abs(brys.get(a, np.nan) - brys.get(b, np.nan)) for a, b, _ in ps])])
        ok = np.all(np.isfinite(ctrl), axis=1)

        block = {"n_pairs": len(ps), "n_pairs_with_concreteness": int(ok.sum()),
                 "frequency_channels_rho": {k: round(v, 4) for k, v in frho.items()},
                 "hardened_frequency_floor": bfreq, "arms": {}}
        for arm, c in cos.items():
            if arm.endswith("_SHUFFLED"):
                continue
            cands = {"HARDENED_FREQUENCY_" + bfreq: fch[bfreq],
                     "A_ORTHOGRAPHIC": cos["A_ORTHOGRAPHIC"]}
            if arm + "_SHUFFLED" in cos:
                cands["OWN_SCRAMBLE"] = cos[arm + "_SHUFFLED"]
            cands.pop(arm, None)
            rf = {k: FT._spearman(v, gold) for k, v in cands.items()}
            bf = max(rf, key=lambda k: rf[k])
            d = FT.boot_rho_diff(c, cands[bf], gold, n_boot=N_BOOT)
            e = {"rho": FT.boot_rho(c, gold, n_boot=N_BOOT),
                 "floor_rho_by_arm": {k: round(v, 4) for k, v in rf.items()},
                 "strongest_floor": bf, "margin_over_strongest_floor": d,
                 "band": FT.band(d["ci95"]),
                 "clears_floor": bool(FT.band(d["ci95"]) == "ABOVE"
                                      and d["point"] >= FT.T_MARGIN_MIN)}
            if ok.sum() > 50:
                e["partial_rho_concreteness_controlled"] = round(
                    PX.partial_spearman(c[ok], gold[ok], ctrl[ok]), 4)
            if arm.startswith("ASSET_") and arm.split("_")[-1] in ("TOKEMB", "ISOL", "CTX"):
                ri = "CTRL_RANDINIT_" + arm.split("_")[-1]
                if ri in cos:
                    dr = FT.boot_rho_diff(c, cos[ri], gold, n_boot=N_BOOT)
                    e["vs_random_init"] = {"arm": ri, "diff": dr, "band": FT.band(dr["ci95"])}
            block["arms"][arm] = e
        block["per_pair_cos"] = {k: [round(float(x), 6) for x in v] for k, v in cos.items()}
        block["gold"] = [float(x) for x in gold]
        results[gold_name] = block
        print(f"[{gold_name}] n={len(ps)} hardened_freq={bfreq}({frho[bfreq]:.3f}) " +
              " ".join(f"{k}={block['arms'][k]['rho']['point']:.3f}"
                       for k in ("ASSET_NORMS12", "ASSET_V2_CTX", "ASSET_V2_ISOL",
                                 "CTRL_RANDINIT_CTX", "A_ORTHOGRAPHIC") if k in block["arms"]),
              flush=True)

    clears = sorted({f"{g}|{a}" for g, b in results.items() for a, e in b["arms"].items()
                     if e["clears_floor"] and a.startswith("ASSET_")})
    out = {"anchor_name": ANCHOR_NAME, "run_mode": "full",
           "scope_disclaimer": ("POWER EXTENSION. The item population is the SimLex+WordSim word "
                               "list, NOT the instrument's frequency-ranked vocabulary. These are "
                               "NOT instrument numbers and may not be quoted as such. Identity "
                               "and bundling are NOT measured here."),
           "verdict": ("ASSET_CLEARS_THE_HARDENED_FLOOR_AT_POWER" if clears
                       else "NO_ASSET_CLEARS_THE_HARDENED_FLOOR_AT_POWER"),
           "arms_clearing": clears,
           "config": {"vocab_size": len(vocab), "K_CTX": K_CTX, "N_BOOT": N_BOOT, "seed": SEED},
           "occurrence_index": occ_stats, "results": results,
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
