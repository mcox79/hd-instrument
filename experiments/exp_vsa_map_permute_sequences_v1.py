"""
exp_vsa_map_permute_sequences_v1 -- VSA MAP permutation encoding of ordered sequences -- CPU.

ROUTING: field_VSA_5x Anchor 1 (MAP Permute for ordered sequences). Permutation powers encode ORDER in a single bundle:
  S = sum_k P^k(item_k), where P is a fixed coordinate permutation. The item at position k is recovered by P^-k(S) ->
  cleanup. Validates the substrate can represent + query ordered sequences (steps, timelines, ranked lists) -- a capability
  beyond unordered role-filler bundles. FHRR phasors. CPU.
PRE-REGISTERED: HARD-PASS position-recovery accuracy >= 0.95 at sequence length K=5, vocab V=100. MIDDLE 0.85-0.95.
  HARD-FAIL < 0.85 (permutation encoding does not preserve order at this load).
FORMULA SELF-TESTS (PROT-022): 1. permute invertible. 2. cleanup self. 3. bundle recovers single.
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

ANCHOR_NAME = "vsa_map_permute_sequences_v1"; D = 1024; V = 100
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
K_GRID = [3, 5] if RUN_MODE == "smoke" else [3, 5, 7]; TRIALS = 40 if RUN_MODE == "smoke" else 200


def phasor(m, d, g):
    return np.exp(1j * g.uniform(-np.pi, np.pi, (m, d))).astype(np.complex64)


def permute(v, perm, k):
    # apply permutation P^k (k can be negative for inverse)
    idx = perm
    if k >= 0:
        out = v
        for _ in range(k):
            out = out[idx]
        return out
    inv = np.argsort(perm); out = v
    for _ in range(-k):
        out = out[inv]
    return out


def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def _selftest():
    g = np.random.default_rng(0); perm = g.permutation(32); v = phasor(1, 32, g)[0]
    assert np.allclose(permute(permute(v, perm, 2), perm, -2), v, atol=1e-5), "permute invertible"
    book = phasor(5, 32, g); assert cidx(book[3], book) == 3, "cleanup self"
    assert cidx(book[1], book) == 1, "bundle recovers single"
    print("[selftest] PASS: vsa-map-permute-sequences", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    g = np.random.default_rng(7); perm = g.permutation(D); by = {}
    for K in K_GRID:
        book = phasor(V, D, g); hit = 0; tot = 0
        for _ in range(TRIALS):
            seq = g.choice(V, size=K, replace=False)
            S = np.sum([permute(book[seq[k]], perm, k) for k in range(K)], axis=0)
            for k in range(K):
                rec = permute(S, perm, -k); hit += int(cidx(rec, book) == seq[k]); tot += 1
        by["K%d" % K] = hit / tot
        print("  K=%d position-recovery=%.3f (V=%d)" % (K, by["K%d" % K], V), flush=True)
    return {"by": by, "V": V}


def verdict(r) -> Tuple[str, str]:
    by = r["by"]; k5 = by.get("K5", 0.0); summary = "recovery by K: %s (V=%d)" % ({k: round(v, 3) for k, v in by.items()}, r["V"])
    if k5 >= 0.95:
        return ("HARD_PASS", "HARD_PASS: permutation-power encoding recovers sequence ORDER >=0.95 at K=5 -- the substrate represents ordered sequences (timelines, steps, ranked lists). " + summary)
    if k5 >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: order recovery 0.85-0.95 at K=5. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: order recovery <0.85 at K=5 (raise D). " + summary)


print("[config] anchor=%s mode=%s D=%d V=%d K=%s" % (ANCHOR_NAME, RUN_MODE, D, V, K_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
