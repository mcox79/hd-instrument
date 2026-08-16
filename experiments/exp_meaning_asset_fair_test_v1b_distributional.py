"""exp_meaning_asset_fair_test_v1b_distributional -- the SECOND family of built-but-unwired
meaning assets: hdlab/random_indexing.py, scored on the UNCHANGED instrument.

Found by enumerating hdlab/ from disk rather than by taking the brief's three named assets on
trust. `hdlab/random_indexing.py` is a complete, substrate-native distributional-semantics encoder
with an `encode(word)` API and THREE context modes, and ORGAN_MAP section B2 already records it as
owned and NOT used ("a RIGHT-OP-WRONG-PLACE *within* this organ"). It has never been scored on an
encoding-quality instrument.

  ASSET_RI_WINDOW   context_mode="window"            canonical Sahlgren bag-of-context
  ASSET_RI_ORDER    order_binding=True               the ORDER-SENSITIVE variant (BEAGLE-style
                                                     cyclic-shift binding) that the live path
                                                     does not use
  ASSET_RI_SYMPAT   context_mode="symmetric_pattern" the 2026-08-06 coordinator-pattern variant

Everything else -- vocabulary, golds, pools, sigmas, seeds, scorers -- is the instrument's,
imported from exp_encoding_quality_instrument_v2 and exp_meaning_asset_fair_test_v1, both UNCHANGED.
Block d = 1024, an instrument-native dimension, with every floor re-run at the same d.

Self-test 0 asserts this cell's metric block reproduces exp_meaning_asset_fair_test_v1.run_unit
EXACTLY on a shared arm, so the duplication cannot silently diverge.

ASCII-only. CPU. No network. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS
import exp_meaning_asset_fair_test_v1 as FT
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "meaning_asset_fair_test_v1b_distributional"
CODE_VERSION = "v1b.0"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_A, _ = _ap.parse_known_args()
SMOKE = bool(_A.smoke)

D_BLOCK = 1024
RI_N = 1024
RI_WINDOW = 5
RI_MIN_COUNT = 5
RI_SPARSITY = 10
RI_MODES = {
    "ASSET_RI_WINDOW": {"context_mode": "window", "order_binding": False},
    "ASSET_RI_ORDER": {"context_mode": "window", "order_binding": True},
    "ASSET_RI_SYMPAT": {"context_mode": "symmetric_pattern", "order_binding": False},
}
FLOORS = ["A_ORTHOGRAPHIC", "A_FREQUENCY"]
REFS = ["A_RANDOM_IID", "A_COLLAPSE", "P_LIVE_WORD"]
ARMS = FLOORS + REFS + sorted(RI_MODES) + [a + "_SHUFFLED" for a in sorted(RI_MODES)]

_RI_CACHE: Dict[str, np.ndarray] = {}
_RI_STATS: Dict[str, Dict] = {}


def corpus_tokens() -> List[str]:
    with open(INS.CORPUS, "rb") as f:
        raw = f.read(INS.CORPUS_BYTES)
    cut = raw.rfind(b"\n")
    if cut > 0:
        raw = raw[:cut]
    return re.findall(r"[a-z]+", raw.decode("utf-8", errors="ignore").lower())


def ri_codes(arm: str, words) -> np.ndarray:
    if arm in _RI_CACHE:
        return _RI_CACHE[arm]
    from hdlab.random_indexing import RandomIndexingEncoder
    kw = RI_MODES[arm]
    t0 = time.time()
    enc = RandomIndexingEncoder(N=RI_N, sparsity=RI_SPARSITY, window=RI_WINDOW,
                                min_count=RI_MIN_COUNT, seed=7, **kw)
    enc.fit_corpus(corpus_tokens())
    X = np.zeros((len(words), RI_N), dtype=np.float32)
    miss = 0
    for i, w in enumerate(words):
        if enc.has(w):
            X[i] = np.asarray(enc.encode(w), dtype=np.float32)
        else:
            miss += 1
            X[i] = 1e-3 * np.random.default_rng(7 ^ i).standard_normal(RI_N)
    _RI_STATS[arm] = {"ri_vocab_size": int(enc.vocab_size()), "n_tokens_seen": int(enc._n_tokens_seen),
                      "n_instrument_words_missing": miss, "fit_s": round(time.time() - t0, 1),
                      "N": RI_N, "window": RI_WINDOW, "min_count": RI_MIN_COUNT, **kw}
    print(f"[ri] {arm} {_RI_STATS[arm]}", flush=True)
    X = INS._l2n(X)
    _RI_CACHE[arm] = X
    return X


def build_codes(arm, d, seed, words, counts, pairs, out_dir):
    if arm in ("A_RANDOM_IID", "A_COLLAPSE", "A_ORTHOGRAPHIC", "P_LIVE_WORD"):
        return INS.build_codes(arm, d, seed, words, pairs, out_dir)[0]
    if arm == "A_FREQUENCY":
        return FT.enc_frequency(words, counts, d, seed)
    core = arm[:-len("_SHUFFLED")] if arm.endswith("_SHUFFLED") else arm
    X = ri_codes(core, words)
    if arm.endswith("_SHUFFLED"):
        X = X[np.random.default_rng(seed ^ 0xC0FFEE).permutation(len(words))]
    return X


def run_unit(arm, d, seed, words, counts, ortho_pool, freq_pool, golds, pairs, w2i, out_dir):
    """Metric block. Self-test 0 asserts this reproduces FT.run_unit exactly."""
    t0 = time.time()
    codes = INS._l2n(build_codes(arm, d, seed, words, counts, pairs, out_dir))
    recov = {}
    for n in INS.N_SWEEP:
        if n > len(words):
            continue
        recov[str(n)] = {f"{s:g}": INS.recoverability(codes, n, s, seed) for s in INS.SIGMAS}
    disc = {"disc_ortho": {f"{s:g}": INS.discriminability(codes, ortho_pool, s, seed)
                           for s in INS.SIGMAS},
            "disc_freq": {f"{s:g}": INS.discriminability(codes, freq_pool, s, seed)
                          for s in INS.SIGMAS}}
    ng = min(INS.N_GATE, len(words))
    onehot = np.eye(len(words), dtype=np.float32)
    signed = INS._l2n(np.sign(codes).astype(np.float32))
    stages = [("S0_ORACLE", INS.recoverability_topb(onehot, ng, INS.SIGMA_GATE, seed, INS.BUNDLE_B)),
              ("S1_ENCODE", INS.recoverability_topb(codes, ng, INS.SIGMA_GATE, seed, INS.BUNDLE_B)),
              ("S2_ENCODE_SIGN", INS.recoverability_topb(signed, ng, INS.SIGMA_GATE, seed,
                                                         INS.BUNDLE_B)),
              ("S3_BUNDLE", INS.bundle_survival(codes, ng, INS.BUNDLE_B, False, seed)),
              ("S4_BUNDLE_SIGN", INS.bundle_survival(codes, ng, INS.BUNDLE_B, True, seed))]
    chain, prev = [], None
    for name, acc in stages:
        bits = INS.fano_bits_list(acc, ng, INS.BUNDLE_B) if acc == acc else float("nan")
        chain.append({"stage": name, "accuracy": acc, "info_bits_lower_bound": bits,
                      "criterion": f"top-{INS.BUNDLE_B} of {ng}",
                      "destroyed_bits_vs_prev": (None if prev is None else prev - bits)})
        prev = bits
    struct, per_probe = {}, {}
    for gname, lab in golds.items():
        a_i, r_i, _ = FT.structure_ap_perprobe(codes, lab, INS.AP_PROBES, seed)
        ap = float(a_i.mean()) if len(a_i) else float("nan")
        ch = float(r_i.mean()) if len(r_i) else float("nan")
        struct[gname] = {"ap": ap, "chance": ch, "lift": (ap / ch if ch > 0 else float("nan")),
                         "n_scored": int(len(a_i))}
        per_probe[gname] = {"ap": a_i.tolist(), "rand": r_i.tolist()}
    rho, n_pairs = INS.simlex_rho(codes, w2i, pairs)
    cs, gs, _ = FT.simlex_perpair(codes, w2i, pairs)
    return {"arm": arm, "d": d, "seed": seed, "d_eff": int(codes.shape[1]),
            "recoverability": recov,
            "sigma_half_at_N_GATE": INS.sigma_half(recov.get(str(ng), {}), INS.SIGMAS),
            "discriminability": disc, "stage_chain": chain, "structure": struct,
            "simlex_rho": rho, "simlex_pairs_covered": n_pairs, "per_probe": per_probe,
            "simlex_cos": cs.tolist(), "simlex_gold": gs.tolist(),
            "elapsed_s": round(time.time() - t0, 1)}


def selftest(words=None, counts=None, ortho=None, freq=None, golds=None, pairs=None, w2i=None,
             out_dir=None) -> None:
    """Self-test 0: this cell's metric block == FT.run_unit on a shared arm, EXACTLY."""
    if words is None:
        w = [f"w{i:04d}" for i in range(300)]
        c = np.array([10 ** (3 - 2 * i / 299.0) for i in range(300)])
        o = INS.build_ortho_neighbours(w, INS.K_DISTRACT)
        f = INS.build_freq_controls(c, o, INS.K_DISTRACT)
        g = {"GOLD_ORTHO": INS.gold_ortho(w), "GOLD_FREQBAND": INS.gold_freqband(c),
             "GOLD_PLANTED": INS.gold_planted(len(w))}
        p = INS.load_simlex(INS.SIMLEX)
        i2 = {x: i for i, x in enumerate(w)}
        od = REPO / "scratch"
        words, counts, ortho, freq, golds, pairs, w2i, out_dir = w, c, o, f, g, p, i2, od
    a = run_unit("A_RANDOM_IID", 64, 7, words, counts, ortho, freq, golds, pairs, w2i, out_dir)
    b = FT.run_unit("A_RANDOM_IID", 64, 7, words, counts, ortho, freq, golds, pairs, w2i, out_dir)
    for k in ("recoverability", "discriminability", "stage_chain", "structure", "simlex_rho"):
        assert json.dumps(a[k], sort_keys=True) == json.dumps(b[k], sort_keys=True), \
            f"metric block diverged from exp_meaning_asset_fair_test_v1 on {k}"
    print("[selftest] v1b metric block == v1 metric block (5 metric groups, exact)", flush=True)


def main() -> int:
    t0 = time.time()
    selftest()
    if _A.self_test:
        return 0
    out_dir = get_output_dir(ANCHOR_NAME + ("_smoke" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    fp = hashlib.sha256(json.dumps({"c": CODE_VERSION, "m": "smoke" if SMOKE else "full",
                                    "V": INS.V, "B": INS.CORPUS_BYTES, "N": RI_N,
                                    "w": RI_WINDOW, "mc": RI_MIN_COUNT,
                                    "seeds": INS.SEEDS}, sort_keys=True).encode()).hexdigest()[:16]
    words, counts = INS.build_vocab(INS.CORPUS, INS.CORPUS_BYTES, INS.V)
    w2i = {w: i for i, w in enumerate(words)}
    ortho = INS.build_ortho_neighbours(words, INS.K_DISTRACT)
    freq = INS.build_freq_controls(counts, ortho, INS.K_DISTRACT)
    golds = {"GOLD_ORTHO": INS.gold_ortho(words), "GOLD_FREQBAND": INS.gold_freqband(counts),
             "GOLD_PLANTED": INS.gold_planted(len(words))}
    pairs = INS.load_simlex(INS.SIMLEX)
    print(f"[cfg] mode={'smoke' if SMOKE else 'full'} V={len(words)} d={D_BLOCK} fp={fp}",
          flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    for arm in ARMS:
        for seed in INS.SEEDS:
            key = unit_key(ANCHOR_NAME, CODE_VERSION, fp, arm, f"d{D_BLOCK}", f"seed{seed}",
                           f"V{INS.V}", f"N{INS.N_GATE}")
            if key in done:
                continue
            res = run_unit(arm, D_BLOCK, seed, words, counts, ortho, freq, golds, pairs, w2i,
                           out_dir)
            record_unit(str(out_dir), key, res)
            units[key] = res
            print(f"[unit] {arm} seed={seed} rho={res['simlex_rho']:.4f} "
                  f"ortho_lift={res['structure']['GOLD_ORTHO']['lift']:.3f} "
                  f"({res['elapsed_s']}s)", flush=True)

    by = {}
    for u in units.values():
        if u.get("arm"):
            by.setdefault(u["arm"], {})[int(u["seed"])] = u

    def agg(arm, path):
        vals = []
        for s in INS.SEEDS:
            cur = by.get(arm, {}).get(s)
            for p in path:
                cur = cur.get(p) if isinstance(cur, dict) else None
                if cur is None:
                    break
            if isinstance(cur, (int, float)) and cur == cur:
                vals.append(float(cur))
        return float(np.mean(vals)) if vals else float("nan")

    reg = [
        {"gate_id": "REG2a", "claim": "A_RANDOM_IID |simlex rho| <= 0.10",
         "observed": abs(agg("A_RANDOM_IID", ["simlex_rho"])), "op": "<=", "threshold": 0.10},
        {"gate_id": "REG2b", "claim": "A_RANDOM_IID GOLD_ORTHO lift <= 1.15",
         "observed": agg("A_RANDOM_IID", ["structure", "GOLD_ORTHO", "lift"]), "op": "<=",
         "threshold": 1.15},
        {"gate_id": "REG3", "claim": "A_COLLAPSE recoverability <= 0.05",
         "observed": agg("A_COLLAPSE", ["recoverability", str(min(INS.N_GATE, INS.V)),
                                        f"{INS.SIGMA_GATE:g}"]), "op": "<=", "threshold": 0.05},
        {"gate_id": "REG4", "claim": "A_ORTHOGRAPHIC GOLD_ORTHO lift >= 3.0",
         "observed": agg("A_ORTHOGRAPHIC", ["structure", "GOLD_ORTHO", "lift"]), "op": ">=",
         "threshold": 3.0},
    ]
    for r in reg:
        v, t = r["observed"], r["threshold"]
        r["passed"] = bool(v == v and ((v <= t) if r["op"] == "<=" else (v >= t)))
    reg_ok = all(r["passed"] for r in reg)

    comparisons = {}
    for arm in sorted(RI_MODES):
        u = by[arm][INS.SEEDS[0]]
        fl = FLOORS + [arm + "_SHUFFLED"]
        fr = {f: agg(f, ["simlex_rho"]) for f in fl}
        bf = max(fr, key=lambda k: (fr[k] if fr[k] == fr[k] else -9))
        gold = u["simlex_gold"]
        d = FT.boot_rho_diff(u["simlex_cos"], by[bf][INS.SEEDS[0]]["simlex_cos"], gold)
        gold_cmp = {}
        for g in golds:
            fli = {f: agg(f, ["structure", g, "lift"]) for f in fl}
            bfg = max(fli, key=lambda k: (fli[k] if fli[k] == fli[k] else -9))
            pp, pf = u["per_probe"][g], by[bfg][INS.SEEDS[0]]["per_probe"][g]
            bd = FT.boot_lift_diff(pp["ap"], pp["rand"], pf["ap"], pf["rand"])
            gold_cmp[g] = {"arm_lift": agg(arm, ["structure", g, "lift"]),
                           "floor_lift_by_arm": fli, "strongest_floor": bfg,
                           "diff_vs_strongest_floor": bd, "band": FT.band(bd["ci95"])}
        ch = u["stage_chain"]
        s2 = next(x["info_bits_lower_bound"] for x in ch if x["stage"] == "S2_ENCODE_SIGN")
        s3 = next(x["info_bits_lower_bound"] for x in ch if x["stage"] == "S3_BUNDLE")
        comparisons[arm] = {
            "IDENTITY": {"sigma_half": agg(arm, ["sigma_half_at_N_GATE"]),
                         "recov_at_N_GATE_sigma1": agg(arm, ["recoverability",
                                                             str(min(INS.N_GATE, INS.V)),
                                                             f"{INS.SIGMA_GATE:g}"]),
                         "disc_freq_minus_disc_ortho_at_sigma8":
                             agg(arm, ["discriminability", "disc_freq", "8"])
                             - agg(arm, ["discriminability", "disc_ortho", "8"])},
            "STRUCTURE_SEMANTIC_SIMLEX": {"arm_rho": FT.boot_rho(u["simlex_cos"], gold),
                                          "strongest_floor": bf, "floor_rho_by_arm": fr,
                                          "diff_vs_strongest_floor": d, "band": FT.band(d["ci95"]),
                                          "clears_floor": bool(FT.band(d["ci95"]) == "ABOVE"
                                                               and d["point"] >= FT.T_MARGIN_MIN)},
            "STRUCTURE_GOLDS": gold_cmp,
            "BUNDLING": {"bits_before_sum_S2": s2, "bits_after_sum_S3": s3,
                         "bits_destroyed_by_the_sum": s2 - s3,
                         "ceiling_bits": math.log2(min(INS.N_GATE, INS.V) / float(INS.BUNDLE_B))},
        }

    any_clear = any(c["STRUCTURE_SEMANTIC_SIMLEX"]["clears_floor"] for c in comparisons.values())
    verdict = ("INVALID_VALIDITY_GATE_FAILED" if not reg_ok else
               "ASSET_CLEARS_THE_STRONGEST_FLOOR" if any_clear else
               "NO_ASSET_CLEARS_THE_STRONGEST_FLOOR")
    per_arm = {a: {"simlex_rho": agg(a, ["simlex_rho"]),
                   "GOLD_ORTHO_lift": agg(a, ["structure", "GOLD_ORTHO", "lift"]),
                   "GOLD_FREQBAND_lift": agg(a, ["structure", "GOLD_FREQBAND", "lift"]),
                   "GOLD_PLANTED_lift": agg(a, ["structure", "GOLD_PLANTED", "lift"]),
                   "sigma_half": agg(a, ["sigma_half_at_N_GATE"])} for a in by}
    metrics = {"anchor_name": ANCHOR_NAME, "run_mode": "smoke" if SMOKE else "full",
               "verdict": verdict, "code_version": CODE_VERSION, "config_fingerprint": fp,
               "instrument": {"module": "experiments/exp_encoding_quality_instrument_v2.py",
                              "edited": False},
               "asset": {"module": "hdlab/random_indexing.py",
                         "why_here": ("built, complete, has encode(word), NEVER scored on an "
                                      "encoding-quality instrument; ORGAN_MAP B2 records the "
                                      "order-sensitive variant as owned and not used"),
                         "modes": RI_MODES},
               "ri_build_stats": _RI_STATS, "validity_gates": reg,
               "validity_gates_all_passed": reg_ok,
               "config": {"d": D_BLOCK, "V": INS.V, "SEEDS": INS.SEEDS,
                          "CORPUS_BYTES": INS.CORPUS_BYTES},
               "per_arm": per_arm, "comparisons": comparisons,
               "elapsed_s": round(time.time() - t0, 1)}
    write_metrics(out_dir, metrics)
    print(json.dumps({"verdict": verdict, "validity_gates_all_passed": reg_ok}, indent=1))
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
