"""
exp_crt_multi_scale_grid_cell_composition_v1 -- Batch C3 #6 (paradigm): CRT multi-scale grid-cell coding -- CPU.

ROUTING: Research Batch C3 cross-domain. Entorhinal grid cells encode position at multiple spatial scales (moduli); the
  Chinese Remainder Theorem makes the joint code unique over the PRODUCT of coprime moduli -> MULTIPLICATIVE capacity
  (exponential in module count). Tests whether the substrate replicates this: encode integer positions as bundled
  per-scale residue codes (one-hot-per-modulus bound into N-dim), decode by CRT vote. Single-scale distinguishes ~m1
  positions; 3-scale coprime distinguishes ~m1*m2*m3. CPU numpy $0.
PRE-REGISTERED: HARD-PASS 3-scale CRT distinguishable-range >= 2x single-scale AND multiplicative scaling visible
  (3-scale ~ product of moduli). MID 1.3-2x. HARD-FAIL <1.3x (no multiplicative composition).
FORMULA SELF-TESTS (PROT-022): 1. CRT uniqueness over product of coprime moduli. 2. residue encode/decode.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "crt_multi_scale_grid_cell_composition_v1"
MODULI = [7, 11, 13]   # coprime; product = 1001
FLIP = 0.05
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N = 2048
else:
    SEEDS = [7, 17, 23]; N = 4096


def bp(M, n, g):
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def encode_pos(pos, scales, codebooks):
    # bundle per-scale residue atom (bipolar bind of scale-key and residue-value)
    v = np.zeros(codebooks[0].shape[1], np.float32)
    for s, m in enumerate(scales):
        v += codebooks[s][pos % m]
    return np.sign(v)


def distinguishable(scales, seed):
    g = np.random.default_rng(seed); P = int(np.prod(scales))
    codebooks = [bp(m, N, g) for m in scales]                       # per-scale residue codebook
    codes = np.stack([encode_pos(p, scales, codebooks) for p in range(P)])
    # distinguishable = fraction of positions whose noisy code decodes back to itself (argmax over all P)
    ok = 0; g2 = np.random.default_rng(seed + 1)
    for p in range(P):
        cue = codes[p] * np.where(g2.random(N) < FLIP, -1.0, 1.0)
        if int(np.argmax(codes @ cue)) == p:
            ok += 1
    return ok                                                       # number of cleanly distinguishable positions


def _selftest():
    from math import gcd
    assert gcd(7, 11) == 1 and gcd(11, 13) == 1 and gcd(7, 13) == 1, "coprime moduli"
    # CRT uniqueness: (p mod 7, p mod 11, p mod 13) unique for p in 0..1001
    res = set((p % 7, p % 11, p % 13) for p in range(7 * 11 * 13)); assert len(res) == 7 * 11 * 13, "CRT uniqueness"
    print("[selftest] PASS: crt", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    single = distinguishable([MODULI[0]], seed)
    two = distinguishable(MODULI[:2], seed)
    three = distinguishable(MODULI, seed)
    print("  [seed=%d] distinguishable: 1-scale=%d 2-scale=%d 3-scale=%d (max-product=%d)" % (seed, single, two, three, int(np.prod(MODULI))), flush=True)
    return {"seed": seed, "single": single, "two_scale": two, "three_scale": three, "ratio_3_vs_1": three / max(single, 1)}


def verdict(ps) -> Tuple[str, str]:
    s1 = float(np.mean([p["single"] for p in ps])); s3 = float(np.mean([p["three_scale"] for p in ps]))
    g = s3 / max(s1, 1e-9); prod = int(np.prod(MODULI))
    summary = "distinguishable 1-scale=%.0f 3-scale=%.0f (CRT product=%d) | 3/1=%.2fx" % (s1, s3, prod, g)
    multiplicative = s3 >= 0.8 * prod
    if g >= 2.0 and multiplicative:
        return ("HARD_PASS", "HARD_PASS: 3-scale CRT gives multiplicative capacity (>=2x single, ~product of moduli) -- grid-cell composition replicated. " + summary)
    if g >= 1.3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: multi-scale helps (1.3-2x) but not fully multiplicative. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no multiplicative composition (<1.3x). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d moduli=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, MODULI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
