"""
exp_resonator_bridge_extractor_v1 -- PRIORITY 0: substrate-native multi-hop via resonator bridge factorization -- CPU.

ROUTING: resonator_bridge_extractor_PRIORITY_0. Iterative decomposition FAILS on natural-language HotpotQA (Qwen-iterative,
  GLiNER, e5 all HF) because reformulated queries lose intent. This tests the substrate-NATIVE path: a 2-hop chain is encoded
  as a single bound hypervector s = e1 * r1 * bridge * r2 * ans (FHRR). Given the KNOWN slots (e1, r1, r2), a resonator network
  factorizes s to recover the UNKNOWN bridge AND answer jointly (one-pass algebraic, no LLM). Measures end-to-end recall@2
  (both bridge + answer correct). SYNTHETIC pre-test; if HP, real HotpotQA encoding is the next gate. Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS resonator recovers both bridge+answer >= 0.50 (substrate-native multi-hop validated synthetically).
  BORDER 0.40-0.50. HARD-FAIL < 0.40 (resonator cannot factorize the bridge chain).
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind inverse. 2. cleanup self. 3. clamped-factor resonance.
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

ANCHOR_NAME = "resonator_bridge_extractor_v1"; N = 2048; NE = 50; NR = 8; MAX_IT = 100
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
TRIALS = 40 if RUN_MODE == "smoke" else 200


def phasor(m, d, g):
    return np.exp(1j * g.uniform(-np.pi, np.pi, (m, d))).astype(np.complex64)


def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def _selftest():
    g = np.random.default_rng(0); a = phasor(1, 32, g)[0]; b = phasor(1, 32, g)[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-4), "bind/unbind inverse"
    book = phasor(5, 32, g); assert cidx(book[2], book) == 2, "cleanup self"
    # clamped resonance: s=a*b, a known -> b = s*conj(a)
    s = a * book[1]; assert cidx(s * np.conj(a), book) == 1, "clamped-factor resonance"
    print("[selftest] PASS: resonator-bridge-extractor", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def resonate_chain(s, e1, r1, r2, Ebook):
    # s = e1 * r1 * bridge * r2 * ans ; e1,r1,r2 clamped (known); solve bridge, ans in Ebook via soft resonator
    known = e1 * r1 * r2
    bridge = Ebook.mean(0); ans = Ebook.mean(0)
    bridge = bridge / (np.abs(bridge) + 1e-8); ans = ans / (np.abs(ans) + 1e-8)
    prev = None
    for _ in range(MAX_IT):
        rb = s * np.conj(known * ans)                       # unbind everything except bridge
        sb = Ebook @ np.conj(rb); bridge = (sb @ Ebook); bridge = bridge / (np.abs(bridge) + 1e-8)
        ra = s * np.conj(known * bridge)                    # unbind everything except ans
        sa = Ebook @ np.conj(ra); ans = (sa @ Ebook); ans = ans / (np.abs(ans) + 1e-8)
        cur = (int(np.argmax(sb.real)), int(np.argmax(sa.real)))
        if cur == prev:
            break
        prev = cur
    return prev


def run() -> Dict:
    g = np.random.default_rng(7); succ_both = 0; succ_bridge = 0
    for _ in range(TRIALS):
        Ebook = phasor(NE, N, g); Rbook = phasor(NR, N, g)
        e1i, bi, ai = g.choice(NE, 3, replace=False); r1i, r2i = g.integers(0, NR), g.integers(0, NR)
        s = Ebook[e1i] * Rbook[r1i] * Ebook[bi] * Rbook[r2i] * Ebook[ai]
        gb, ga = resonate_chain(s, Ebook[e1i], Rbook[r1i], Rbook[r2i], Ebook)
        succ_bridge += int(gb == bi); succ_both += int(gb == bi and ga == ai)
    n = TRIALS; r = {"recall2": succ_both / n, "bridge_recall": succ_bridge / n, "n": n}
    print("  resonator multi-hop: bridge-recall=%.3f both(bridge+ans)recall@2=%.3f (NE=%d NR=%d N=%d, n=%d)" % (r["bridge_recall"], r["recall2"], NE, NR, N, n), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    rc = r["recall2"]; s = "recall@2(both)=%.3f bridge-recall=%.3f (n=%d)" % (rc, r["bridge_recall"], r["n"])
    if rc >= 0.50:
        return ("HARD_PASS", "HARD_PASS: resonator factorizes the bridge+answer chain >=0.50 from a VSA-encoded multi-hop query -- substrate-NATIVE multi-hop works algebraically (no LLM decomposition); real-HotpotQA encoding is the next gate. " + s)
    if rc >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: resonator multi-hop 0.40-0.50 -- partial; tune resonator/codebook size. " + s)
    return ("HARD_FAIL", "HARD_FAIL: resonator cannot factorize the bridge chain (<0.40). " + s)


print("[config] anchor=%s mode=%s N=%d NE=%d NR=%d trials=%d" % (ANCHOR_NAME, RUN_MODE, N, NE, NR, TRIALS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
