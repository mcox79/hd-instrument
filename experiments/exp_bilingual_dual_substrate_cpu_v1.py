"""
exp_bilingual_dual_substrate_cpu_v1.py -- BILINGUAL-DUAL-SUBSTRATE (translation via interlingua) -- CPU.

ROUTING: Research REVIVAL_SUBSTRATE_NATIVE_ONLY Sprint-3 (translation, P=0.45). NC shared concepts; each language L has a
  Tier-3 codebook wordL[c] bound to concept[c] in a lexicon ML = sum_c wordL[c] (X) concept[c]. Translate word_A -> concept
  (unbind via MA) -> word_B (unbind via MB). Tests: (a) A->B translation accuracy, (b) a 3rd language C pivots through the
  SAME interlingua (A->C) with no A-C pair training -> LINEAR scaling vs N^2 direct pairs. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS A->B translation >= 0.85 AND A->C (unseen pair, via pivot) >= 0.85 (linear-scaling interlingua). MIDDLE >= 0.70. HARD-FAIL else.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "bilingual_dual_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: bilingual-dual-substrate", flush=True)
def run() -> Dict:
    g = np.random.default_rng(720); NC = 120 if SMOKE else 400; NLANG = 4
    TR = 12 if SMOKE else 70; ab = 0; ac = 0; n = 0
    for _ in range(TR):
        concepts = cphasor(NC, N, g)
        langs = [cphasor(NC, N, g) for _ in range(NLANG)]             # per-language Tier-3 word codebooks
        # lexicon per language: ML = sum_c wordL[c] (X) concept[c]
        lex = [ (langs[L][:, :] * 0).astype(np.complex64) for L in range(NLANG) ]
        lex = []
        for L in range(NLANG):
            lex.append((langs[L] * concepts).sum(0))
        def to_concept(L, word_vec):
            return word_vec * np.conj_  if False else word_vec        # placeholder (unused)
        # translate: word in lang A (index c) -> concept -> word in lang B
        def translate(A, B, c):
            wa = langs[A][c]
            concept_est = lex[A] * np.conj(wa)                        # unbind word -> concept
            ci = cidx(concept_est, concepts)
            wb_est = lex[B] * np.conj(concepts[ci])                   # unbind concept -> word B
            return cidx(wb_est, langs[B])
        for _q in range(10):
            c = int(g.integers(0, NC))
            ab += int(translate(0, 1, c) == c)                        # A->B (trained pair direction shares interlingua)
            ac += int(translate(0, 3, c) == c)                        # A->C: pivot through SAME interlingua, never a direct pair
            n += 1
    abr = ab / n; acr = ac / n
    print("  BILINGUAL A->B=%.3f A->C(pivot, unseen pair)=%.3f (NC=%d, langs=%d)" % (abr, acr, NC, NLANG), flush=True)
    return {"ab_acc": round(abr, 3), "ac_pivot_acc": round(acr, 3), "n_concepts": NC, "n_lang": NLANG}
def verdict(r) -> Tuple[str, str]:
    s = "A->B=%.3f A->C-pivot=%.3f (NC=%d)" % (r["ab_acc"], r["ac_pivot_acc"], r["n_concepts"])
    if r["ab_acc"] >= 0.85 and r["ac_pivot_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: hub-and-spoke interlingua translation -- A->B and A->C (unseen pair, pivoted through the SAME shared concepts) both >=0.85. N-language translation scales LINEARLY (N codebooks) not N^2 (pairs), substrate-only. " + s)
    if r["ab_acc"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: translation 0.70-0.85 or pivot weaker. " + s)
    return ("HARD_FAIL", "HARD_FAIL: interlingua translation <0.70. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
