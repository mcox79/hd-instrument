"""exp_meaning_asset_power_extension_v1 -- POWER EXTENSION to exp_meaning_asset_fair_test_v1.

WHY THIS EXISTS, STATED HONESTLY: the like-for-like arm in the main cell is scored on the
INSTRUMENT'S vocabulary (the 4,096 most frequent corpus surface forms), where SimLex-999 covers
only ~322 of 999 pairs and the Spearman standard error is ~0.06. v2 already disclosed that at that
n its own production rho (0.1048) could not be separated from zero. A null there is therefore
ambiguous between "no signal" and "no power".

THIS CELL IS NOT THE LIKE-FOR-LIKE ARM AND ITS NUMBERS MAY NOT BE QUOTED AS INSTRUMENT NUMBERS.
It changes exactly one thing -- the item population -- to buy power: the vocabulary is the union of
the SimLex-999 and WordSim353 word lists, so up to 999 + 353 pairs are scorable by every arm on
IDENTICAL pairs. Everything else (encoders, pooling, corpus, occurrence rule, cosine, Spearman,
bootstrap) is imported from the main cell or the instrument, not reimplemented.

Reported per arm: rho with a 95% bootstrap CI, the paired-bootstrap DIFFERENCE against the
strongest floor (max of orthographic / frequency / that arm's own scramble), the trained-vs-
random-init difference, and a CONCRETENESS-CONTROLLED partial rho (a concreteness confound has
inflated a learned-encoder result on this project before).

ASCII-only. CPU. No network. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS
import exp_meaning_asset_fair_test_v1 as FT
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "meaning_asset_power_extension_v1"
WORDSIM = REPO / "data" / "encoder_eval_benchmarks" / "wordsim353_combined.csv"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_A, _ = _ap.parse_known_args()
SMOKE = bool(_A.smoke)
K_CTX = 4 if SMOKE else 8
N_BOOT = 500 if SMOKE else 10000
SEED = 7


def load_wordsim(path: Path) -> List[Tuple[str, str, float]]:
    out = []
    if not path.exists():
        return out
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            ks = list(row.keys())
            try:
                out.append((row[ks[0]].strip().lower(), row[ks[1]].strip().lower(),
                            float(row[ks[2]])))
            except (ValueError, IndexError, TypeError):
                continue
    return out


def corpus_counts(words: Sequence[str]) -> np.ndarray:
    want = {w: i for i, w in enumerate(words)}
    c = np.zeros(len(words), dtype=np.float64)
    with open(INS.CORPUS, "rb") as f:
        raw = f.read(INS.CORPUS_BYTES)
    cut = raw.rfind(b"\n")
    if cut > 0:
        raw = raw[:cut]
    for tok in re.findall(r"[a-z]+", raw.decode("utf-8", errors="ignore").lower()):
        i = want.get(tok)
        if i is not None:
            c[i] += 1.0
    return c


def _rank(x):
    x = np.asarray(x, dtype=np.float64)
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x), dtype=np.float64)
    r[order] = np.arange(len(x), dtype=np.float64)
    xs = x[order]
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[i]:
            j += 1
        if j > i:
            r[order[i:j + 1]] = np.mean(r[order[i:j + 1]])
        i = j + 1
    return r


def partial_spearman(a, b, controls: np.ndarray) -> float:
    """Spearman(a, b) after linearly removing `controls` from BOTH rank vectors."""
    ra, rb = _rank(a), _rank(b)
    C = np.column_stack([np.ones(len(ra))] + [_rank(controls[:, k])
                                              for k in range(controls.shape[1])])
    def resid(y):
        beta, *_ = np.linalg.lstsq(C, y, rcond=None)
        return y - C @ beta
    ea, eb = resid(ra), resid(rb)
    den = float(np.sqrt((ea @ ea) * (eb @ eb)))
    return float(ea @ eb / den) if den > 0 else float("nan")


def main() -> int:
    t0 = time.time()
    simlex = INS.load_simlex(INS.SIMLEX)
    wordsim = load_wordsim(WORDSIM)
    from hdlab import grounded_similarity as GS
    norms = GS._table()
    brys = FT.brysbaert_conc()

    vocab = sorted({w for a, b, _ in simlex + wordsim for w in (a, b)})
    if SMOKE:
        vocab = vocab[:200]
    w2i = {w: i for i, w in enumerate(vocab)}
    counts = corpus_counts(vocab)
    print(f"[vocab] {len(vocab)} words; in-corpus {int((counts > 0).sum())}; "
          f"in-norms {sum(1 for w in vocab if w in norms)}", flush=True)

    # occurrence index for the _CTX read-out, same rule as the main cell
    occ, occ_stats = FT.build_occurrences(vocab, K_CTX)
    print(f"[occ] {occ_stats}", flush=True)

    codes: Dict[str, np.ndarray] = {}
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
    codes["A_FREQUENCY"] = FT.enc_frequency(vocab, counts, 512, SEED)
    codes["A_RANDOM_IID"] = INS.enc_random_iid(vocab, 512, SEED)
    codes["P_LIVE_WORD"] = INS.enc_live_word(vocab, 256, SEED)
    codes["CTRL_CONCRETENESS_ONLY"] = FT.enc_concreteness_only(vocab, 512, SEED)
    for a in ("ASSET_V2_CTX", "ASSET_RETRAIN_CTX", "CTRL_RANDINIT_CTX", "ASSET_NORMS12",
              "ASSET_V2_ISOL", "ASSET_V2_TOKEMB"):
        codes[a + "_SHUFFLED"] = codes[a][np.random.default_rng(SEED ^ 0xC0FFEE)
                                          .permutation(len(vocab))]

    results = {}
    for gold_name, pairs in (("SIMLEX999", simlex), ("WORDSIM353", wordsim)):
        # PRIMARY pair set: both words covered by the NORMS table, so every arm scores the SAME
        # pairs (the norms are the only arm with real coverage gaps).
        sel = [(a, b, s) for a, b, s in pairs
               if a in w2i and b in w2i and a in norms and b in norms]
        allp = [(a, b, s) for a, b, s in pairs if a in w2i and b in w2i]
        for setname, ps in (("BOTH_IN_NORMS", sel), ("ALL_COVERED", allp)):
            if len(ps) < 20:
                continue
            gold = np.array([s for _, _, s in ps])
            cos = {k: np.array([float(V[w2i[a]] @ V[w2i[b]]) for a, b, _ in ps])
                   for k, V in codes.items()}
            ctrl = np.column_stack([
                np.array([0.5 * (brys.get(a, np.nan) + brys.get(b, np.nan)) for a, b, _ in ps]),
                np.array([abs(brys.get(a, np.nan) - brys.get(b, np.nan)) for a, b, _ in ps])])
            ok = np.all(np.isfinite(ctrl), axis=1)
            block = {"n_pairs": len(ps), "n_pairs_with_concreteness": int(ok.sum()), "arms": {}}
            floors = ["A_ORTHOGRAPHIC", "A_FREQUENCY"]
            for arm, c in cos.items():
                fl = list(floors) + ([arm + "_SHUFFLED"] if arm + "_SHUFFLED" in cos else [])
                fr = {f: FT._spearman(cos[f], gold) for f in fl}
                bf = max(fr, key=lambda k: fr[k])
                d = FT.boot_rho_diff(c, cos[bf], gold, n_boot=N_BOOT)
                entry = {"rho": FT.boot_rho(c, gold, n_boot=N_BOOT),
                         "strongest_floor": bf, "floor_rho": fr,
                         "diff_vs_strongest_floor": d, "band": FT.band(d["ci95"])}
                if ok.sum() > 30:
                    entry["partial_rho_concreteness_controlled"] = partial_spearman(
                        c[ok], gold[ok], ctrl[ok])
                if arm.startswith("ASSET_") and not arm.endswith("_SHUFFLED"):
                    ri = "CTRL_RANDINIT_" + arm.split("_")[-1]
                    if ri in cos:
                        dr = FT.boot_rho_diff(c, cos[ri], gold, n_boot=N_BOOT)
                        entry["vs_random_init"] = {"arm": ri, "diff": dr,
                                                   "band": FT.band(dr["ci95"])}
                block["arms"][arm] = entry
            results[f"{gold_name}|{setname}"] = block
            print(f"[{gold_name}|{setname}] n={len(ps)} "
                  + " ".join(f"{k}={block['arms'][k]['rho']['point']:.3f}"
                             for k in ("ASSET_NORMS12", "ASSET_V2_CTX", "CTRL_RANDINIT_CTX",
                                       "A_ORTHOGRAPHIC", "A_FREQUENCY") if k in block["arms"]),
                  flush=True)

    out_dir = get_output_dir(ANCHOR_NAME + ("_smoke" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = {"anchor_name": ANCHOR_NAME, "run_mode": "smoke" if SMOKE else "full",
               "scope_disclaimer": ("POWER EXTENSION. The item population is the SimLex+WordSim "
                                    "word list, NOT the instrument's frequency-ranked vocabulary. "
                                    "These numbers are NOT instrument numbers and may not be "
                                    "quoted as such. Identity and bundling axes are NOT measured "
                                    "here."),
               "config": {"vocab_size": len(vocab), "K_CTX": K_CTX, "N_BOOT": N_BOOT,
                          "seed": SEED, "corpus_bytes": INS.CORPUS_BYTES},
               "occurrence_index": occ_stats, "results": results,
               "elapsed_s": round(time.time() - t0, 1)}
    write_metrics(out_dir, metrics)
    print(f"[done] {out_dir}/metrics.json ({metrics['elapsed_s']}s)", flush=True)
    return 0


if __name__ == "__main__":
    if _A.self_test:
        g = np.random.default_rng(0)
        # CASE 1 -- a genuine CONFOUND: x and y are correlated ONLY through c. Partial rho must
        # collapse toward 0. (The first version of this test used a control that was independent
        # of x and predictive of y, which legitimately RAISES partial rho -- the assertion was
        # wrong, not the function. Kept as CASE 3 so the distinction stays visible.)
        c = g.random(400)
        x = c + 0.10 * g.standard_normal(400)
        y = c + 0.10 * g.standard_normal(400)
        full = FT._spearman(x, y)
        part = partial_spearman(x, y, c[:, None])
        assert full > 0.75, f"confound setup broken, full rho {full}"
        assert abs(part) < 0.25, f"partial rho did not remove the confound ({part} vs {full})"
        # CASE 2 -- a constant control must not move rho at all
        assert abs(partial_spearman(x, y, np.zeros((400, 1))) - full) < 1e-9, "null control moved rho"
        # CASE 3 -- an independent-of-x predictor of y RAISES partial rho (variance removed)
        x3 = g.random(400)
        c3 = g.random(400)
        y3 = 0.6 * x3 + 0.8 * c3 + 0.1 * g.standard_normal(400)
        assert partial_spearman(x3, y3, c3[:, None]) > FT._spearman(x3, y3), "case 3 direction"
        print("[selftest] power-extension PASS (3 cases)")
        sys.exit(0)
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:                                          # noqa: BLE001 -- printed, not hidden
        import traceback
        traceback.print_exc()
        sys.exit(2)
