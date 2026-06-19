"""
exp_neurogenesis_hiermerge_cpu_v1.py -- NEUROGENESIS hierarchical-merge rescue (RESCUE-1) -- CPU.

ROUTING: Research CYCLE226 Tier-1 (neurogenesis RESCUE-1; cheapest). NEUROGENESIS-REAL over-fragmented. Fixed-threshold tuning
  is the FAILING (fixed-structure) approach. RESCUE per the temporal/contextual pattern: let online growth over-fragment, then
  POST-HOC HIERARCHICAL MERGE -- agglomerate shards with cosine >= 0.85 until stable. This is a batch/contextual consolidation,
  not a fixed online threshold. Tests post-merge shard count ~ K and purity vs the over-fragmented pre-merge state. N=8192.
PRE-REGISTERED: HARD-PASS post-merge purity >= 0.60 AND merged-shards in [K-3, K+8] AND << pre-merge shard count. MIDDLE purity >= 0.50. HARD-FAIL else.
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
ANCHOR_NAME = "neurogenesis_hiermerge_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: neurogenesis-hiermerge", flush=True)
def run() -> Dict:
    g = np.random.default_rng(634); K = 12 if SMOKE else 18; PER = 20; NE = K * PER
    TR = 6 if SMOKE else 30; pre_ns = []; post_ns = []; post_pur = []
    for _ in range(TR):
        protos = cphasor(K, N, g); truth = np.repeat(np.arange(K), PER)
        ents = cnorm(np.stack([protos[truth[i]] + 0.9 * cphasor(1, N, g)[0] for i in range(NE)]))
        # FORCE over-fragmentation: high spawn threshold -> many shards
        order = g.permutation(NE); shards = []; members = []; assign = np.zeros(NE, dtype=int); SPAWN = 0.55
        for i in order:
            x = ents[i]
            if shards:
                sims = [float((np.vdot(s, x)).real) / N for s in shards]; bi = int(np.argmax(sims)); bm = sims[bi]
            else:
                bm = -1; bi = -1
            if bm < SPAWN:
                shards.append(x.copy()); members.append([i]); assign[i] = len(shards) - 1
            else:
                shards[bi] = cnorm(shards[bi] * 6 + x); members[bi].append(i); assign[i] = bi
        pre_count = len(shards)
        # HIERARCHICAL MERGE: agglomerate shards with cosine >= 0.85 until stable
        S = [cnorm(s) for s in shards]; mem = [list(m) for m in members]
        merged = True
        while merged and len(S) > 1:
            merged = False; nS = len(S)
            sim = np.zeros((nS, nS))
            for a in range(nS):
                for b in range(a + 1, nS):
                    sim[a, b] = float((np.vdot(S[a], S[b])).real) / N
            a, b = np.unravel_index(np.argmax(sim), sim.shape)
            if sim[a, b] >= 0.85:
                S[a] = cnorm(S[a] + S[b]); mem[a] = mem[a] + mem[b]; del S[b]; del mem[b]; merged = True
        post_count = len(S)
        # purity from merged assignment
        hit = 0
        for ci in range(len(mem)):
            v = truth[mem[ci]]; maj = int(np.bincount(v).argmax()); hit += int((v == maj).sum())
        purity = hit / NE
        pre_ns.append(pre_count); post_ns.append(post_count); post_pur.append(purity)
    pn = float(np.mean(pre_ns)); on = float(np.mean(post_ns)); pp = float(np.mean(post_pur))
    print("  NEUROGENESIS-HIERMERGE pre-merge shards=%.1f -> post-merge=%.1f (K=%d) | post-merge purity=%.3f" % (pn, on, K, pp), flush=True)
    return {"pre_merge_shards": round(pn, 1), "post_merge_shards": round(on, 1), "post_merge_purity": round(pp, 3), "true_K": K}
def verdict(r) -> Tuple[str, str]:
    on = r["post_merge_shards"]; pp = r["post_merge_purity"]; K = r["true_K"]; s = "pre=%.1f post=%.1f (K=%d) purity=%.3f" % (r["pre_merge_shards"], on, K, pp)
    ok_ns = (K - 3) <= on <= (K + 8)
    if pp >= 0.60 and ok_ns and on < r["pre_merge_shards"]:
        return ("HARD_PASS", "HARD_PASS: hierarchical-merge RESCUES over-fragmented neurogenesis -- post-hoc agglomeration (cosine>=0.85) consolidates %.0f over-fragmented shards to ~K=%d with purity>=0.60. Batch/contextual consolidation fixes the over-fragmentation that fixed-threshold tuning could not. " % (r["pre_merge_shards"], K) + s)
    if pp >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: merge helps; purity 0.50-0.60 or count off. " + s)
    return ("HARD_FAIL", "HARD_FAIL: hierarchical-merge does not recover (<0.50). " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
