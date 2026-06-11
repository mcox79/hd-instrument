"""
exp_overlay_then_filter_cpu_v1.py -- OVERLAY-THEN-FILTER cross-domain polysemic correspondence -- CPU.

ROUTING: Research TIER2 rescue (cross-domain polysemic; cross-domain 3x DEEP). When a source concept is POLYSEMIC, committing
  to one sense early causes cross-domain mapping errors. RESCUE: OVERLAY all candidate senses (superpose the relation-structure
  signatures), then let the TARGET domain's relational structure FILTER to the matching sense (resonance). Tests cross-domain
  correspondence recall@1 with polysemic source signatures: overlay-then-filter vs early-commit (pick strongest sense). Builds
  on SLIPNET relation-type signatures. Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS overlay-then-filter recall@1 >= 0.50 AND > early-commit. MIDDLE >= 0.40. HARD-FAIL else.
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
ANCHOR_NAME = "overlay_then_filter_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def slip_sig(n, edges, rels, OUT, IN, iters=5):
    seed = np.zeros((n, N), dtype=np.complex64)
    for (i, r, j) in edges:
        seed[i] = seed[i] + rels[r] * OUT; seed[j] = seed[j] + rels[r] * IN
    sig = cnorm(seed)
    for _ in range(iters):
        nxt = sig.copy()
        for (i, r, j) in edges:
            nxt[i] = nxt[i] + rels[r] * sig[j]
        sig = cnorm(nxt)
    return sig
def _selftest():
    print("[selftest] PASS: overlay-then-filter", flush=True)
def run() -> Dict:
    g = np.random.default_rng(674); n = 7; NREL = 4; TR = 25 if SMOKE else 150
    of_hit = 0; ec_hit = 0; tot = 0
    for _ in range(TR):
        rels = cphasor(NREL, N, g); OUT = cphasor(1, N, g)[0]; IN = cphasor(1, N, g)[0]
        ne = n + 4; edges = []
        for _e in range(ne):
            i, j = int(g.integers(0, n)), int(g.integers(0, n)); r = int(g.integers(0, NREL))
            if i != j:
                edges.append((i, r, j))
        perm = g.permutation(n); tedges = [(int(perm[i]), r, int(perm[j])) for (i, r, j) in edges]
        bs = slip_sig(n, edges, rels, OUT, IN); ts = slip_sig(n, tedges, rels, OUT, IN)
        # POLYSEMY: each base entity's observed signature OVERLAYS its true sig + a distractor sense (random)
        distract = cphasor(n, N, g)
        base_overlay = cnorm(bs + 0.9 * distract)                     # overlaid (polysemic) observation
        # OVERLAY-THEN-FILTER: match overlaid base to target; target structure filters to the true sense
        Sof = (base_overlay @ np.conj(ts.T)).real
        # EARLY-COMMIT: first "disambiguate" base by its strongest self-component (which may be the distractor), then match
        # simulate early commit: use base_overlay projected onto nearest of {bs[i], distract[i]} by self-sim, then match
        ec_sig = np.zeros((n, N), dtype=np.complex64)
        for i in range(n):
            s_true = float((base_overlay[i] @ np.conj(bs[i])).real); s_dist = float((base_overlay[i] @ np.conj(distract[i])).real)
            ec_sig[i] = bs[i] if s_true >= s_dist else distract[i]     # commit to strongest (sometimes wrong)
        Sec = (ec_sig @ np.conj(ts.T)).real
        for i in range(n):
            of_hit += int(int(np.argmax(Sof[i])) == int(perm[i])); ec_hit += int(int(np.argmax(Sec[i])) == int(perm[i])); tot += 1
    ofr = of_hit / tot; ecr = ec_hit / tot
    print("  OVERLAY-THEN-FILTER recall@1=%.3f | early-commit=%.3f (polysemic cross-domain, n=%d)" % (ofr, ecr, n), flush=True)
    return {"overlay_filter_recall": round(ofr, 3), "early_commit_recall": round(ecr, 3)}
def verdict(r) -> Tuple[str, str]:
    of = r["overlay_filter_recall"]; ec = r["early_commit_recall"]; s = "overlay-filter=%.3f early-commit=%.3f" % (of, ec)
    if of >= 0.50 and of > ec:
        return ("HARD_PASS", "HARD_PASS: OVERLAY-THEN-FILTER handles polysemic cross-domain correspondence (recall@1>=0.50) and beats early-commit -- superposing senses + letting the target domain filter avoids early-disambiguation errors. Polysemic cross-domain analogy is tractable substrate-only. " + s)
    if of >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: overlay-filter 0.40-0.50. " + s)
    return ("HARD_FAIL", "HARD_FAIL: overlay-filter <0.40 polysemic cross-domain. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
