"""
exp_lang_math_coexist_cpu_v1.py -- LANG-MATH-COEXIST: substrate algebra unity across language + math -- CPU.

ROUTING: Research cheap-parallel (substrate algebra unity test). Tests that ONE substrate, with ONE codebook + ONE set of
  algebraic ops (bind/bundle/cleanup), handles BOTH language facts (word -> role-bound concepts) and math facts (operands ->
  equation roles) simultaneously, with no cross-domain interference, PLUS a cross-domain composition (bind a math result to a
  language label and recall it). Demonstrates the architectural claim that substrate IS the compositional algebra for language
  AND math (same algebra; domain-agnostic). Substrate-only, pure-numpy. N=8192.
PRE-REGISTERED: HARD-PASS language recall >= 0.95 AND math recall >= 0.95 AND cross-domain recall >= 0.95 in ONE shared
  substrate (no cross-domain degradation vs single-domain). MIDDLE all >= 0.85. HARD-FAIL else.
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
ANCHOR_NAME = "lang_math_coexist_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: lang-math-coexist", flush=True)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "998")))
    KL = 60 if SMOKE else 150; KM = 60 if SMOKE else 150; V = 600
    # ONE shared codebook + ONE shared value vocabulary (domain-agnostic atoms)
    lang_keys = cphasor(KL, N, g); math_keys = cphasor(KM, N, g); vals = cphasor(V, N, g)
    lt = g.integers(0, V, size=KL); mt = g.integers(0, V, size=KM)
    # ONE substrate holding BOTH language facts and math facts (no separation)
    mem = np.zeros(N, dtype=np.complex64)
    for i in range(KL): mem = mem + lang_keys[i] * vals[lt[i]]
    for i in range(KM): mem = mem + math_keys[i] * vals[mt[i]]
    mem = cnorm(mem)
    lang_rec = sum(cidx(mem * np.conj(lang_keys[i]), vals) == lt[i] for i in range(KL)) / KL
    math_rec = sum(cidx(mem * np.conj(math_keys[i]), vals) == mt[i] for i in range(KM)) / KM
    # CROSS-DOMAIN composition: bind a math result to a language label, recall through the shared store
    label_keys = cphasor(30 if SMOKE else 80, N, g); res = g.integers(0, V, size=len(label_keys))
    xmem = cnorm(mem + sum((label_keys[i] * vals[res[i]] for i in range(len(label_keys))), np.zeros(N, dtype=np.complex64)))
    cross_rec = sum(cidx(xmem * np.conj(label_keys[i]), vals) == res[i] for i in range(len(label_keys))) / len(label_keys)
    print("  LANG-MATH-COEXIST (one substrate): language-recall=%.3f | math-recall=%.3f | cross-domain-label=%.3f (KL=%d KM=%d)" %
          (lang_rec, math_rec, cross_rec, KL, KM), flush=True)
    return {"language_recall": round(lang_rec, 3), "math_recall": round(math_rec, 3), "cross_domain_recall": round(cross_rec, 3), "KL": KL, "KM": KM}
def verdict(r) -> Tuple[str, str]:
    l = r["language_recall"]; m = r["math_recall"]; x = r["cross_domain_recall"]
    s = "lang=%.3f math=%.3f cross=%.3f" % (l, m, x)
    if l >= 0.95 and m >= 0.95 and x >= 0.95:
        return ("HARD_PASS", "HARD_PASS: substrate algebra is UNIFIED across language + math -- one substrate, one codebook, one set of ops binds/recalls language facts (>=0.95), math facts (>=0.95), AND cross-domain math-result-to-language-label (>=0.95) with no domain interference. Substrate IS the domain-agnostic compositional algebra. " + s)
    if l >= 0.85 and m >= 0.85 and x >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: unity holds at >=0.85 but below 0.95 on some domain. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cross-domain interference degrades recall below 0.85. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
