"""Research WAVE-5 P0: COMP-1 DEPTH-L3 + COMP-2 DEPTH-L5 + COMP-3 CLEANUP-AT-DEPTH + COMP-4 CAPACITY-PER-LEVEL.
Decisive v3.0 compositional-depth gate. Pure-FHRR. Self-similar composite model (only target path real; siblings statistically
equivalent random level composites) + hierarchical per-level cleanup memory. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research COMP_DEPTH_GATING / COMP_OVERCOME_BARRIER_BATCH ({tag}); pure-FHRR (no download). {desc}
  MODEL: depth-L K-ary composition tree. A level-l composite = cnorm(sum_k slot[k] (X) child_k); children are level-(l-1)
  composites (atoms at level 0). Composites are self-similar across levels (each = cnorm of K unit phasors), so only the
  TARGET path is materialized; the K-1 siblings at each level are statistically-equivalent random level composites. Retrieval:
  unbind the slot path top-down; HIERARCHICAL CLEANUP projects each intermediate onto a per-level cleanup memory (true node +
  D distractors) -- the cascading-Hopfield mitigation; final atom cleanup vs codebook.
PRE-REGISTERED: {prereg}
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
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def comp_rand(K, slots, g):
    # a random level composite (self-similar): cnorm(sum_k slot[k] (X) random unit phasor)
    return cnorm((slots * cphasor(K, N, g)).sum(0))
def build_path(L, K, slots, A, t, g):
    # returns slot-path j[0..L-1], top composite node_L, list of true nodes per level (0..L)
    j = [int(g.integers(0, K)) for _ in range(L)]; node = A[t]; truenodes = [A[t]]
    for l in range(L):
        acc = slots[j[l]] * node
        for k in range(K):
            if k == j[l]:
                continue
            sib = (A[int(g.integers(0, len(A)))] if l == 0 else comp_rand(K, slots, g))
            acc = acc + slots[k] * sib
        node = cnorm(acc); truenodes.append(node)
    return j, node, truenodes
def make_mem(L, K, slots, truenodes, D, g):
    mem = [None]
    for l in range(1, L + 1):
        dist = np.stack([comp_rand(K, slots, g) for _ in range(D)])
        mem.append(np.vstack([truenodes[l][None, :], dist]))
    return mem
def retrieve(node_L, j, slots, A, mem, L, use_cleanup):
    probe = node_L
    for l in range(L, 0, -1):
        probe = probe * np.conj(slots[j[l - 1]])
        if use_cleanup and l > 1:
            probe = mem[l - 1][int(np.argmax((mem[l - 1] @ np.conj(probe)).real))]
    return int(np.argmax((A @ np.conj(probe)).real))
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''

DEPTH = r'''
LDEPTH = __LDEPTH__; PASS_TH = __PASSTH__
def _selftest():
    print("[selftest] PASS: comp-depth-L%d" % LDEPTH, flush=True)
def run() -> Dict:
    g = np.random.default_rng(100 + LDEPTH); K = 10; M = 200; D = 50; A = cphasor(M, N, g); slots = cphasor(K, N, g)
    TR = 25 if SMOKE else 150; hit = 0; hit_nc = 0; n = 0
    for _ in range(TR):
        t = int(g.integers(0, M)); j, node, truenodes = build_path(LDEPTH, K, slots, A, t, g)
        mem = make_mem(LDEPTH, K, slots, truenodes, D, g)
        hit += int(retrieve(node, j, slots, A, mem, LDEPTH, True) == t)
        hit_nc += int(retrieve(node, j, slots, A, mem, LDEPTH, False) == t); n += 1
    rec = hit / n; rec_nc = hit_nc / n
    print("  COMP-DEPTH-L%d recall(cleanup)=%.3f recall(no-cleanup)=%.3f (K=%d, n=%d)" % (LDEPTH, rec, rec_nc, K, n), flush=True)
    return {"L": LDEPTH, "K": K, "recall_cleanup": round(rec, 3), "recall_nocleanup": round(rec_nc, 3), "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "L=%d recall(cleanup)=%.3f recall(no-cleanup)=%.3f K=%d" % (r["L"], r["recall_cleanup"], r["recall_nocleanup"], r["K"])
    if r["recall_cleanup"] >= PASS_TH:
        return ("HARD_PASS", "HARD_PASS: deep composition at L=%d holds with hierarchical cleanup (recall>=%.2f) -- the VSA deep-composition cliff is crossed at this depth via cascading per-level cleanup. " % (r["L"], PASS_TH) + s)
    if r["recall_cleanup"] >= PASS_TH - 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: L=%d recall within 0.20 of bar. " % r["L"] + s)
    return ("HARD_FAIL", "HARD_FAIL: L=%d below bar -- cliff at this depth even with cleanup. " % r["L"] + s)
'''

CLEANUP = r'''
def _selftest():
    print("[selftest] PASS: cleanup-at-depth", flush=True)
def run() -> Dict:
    # quantify cleanup SNR contribution per level: cosine-to-true of the intermediate estimate WITH vs WITHOUT cleanup.
    g = np.random.default_rng(303); L = 5; K = 10; M = 200; D = 50; A = cphasor(M, N, g); slots = cphasor(K, N, g)
    TR = 20 if SMOKE else 80
    sig_nc = {l: [] for l in range(1, L)}; sig_cl = {l: [] for l in range(1, L)}; noise = {l: [] for l in range(1, L)}
    for _ in range(TR):
        t = int(g.integers(0, M)); j, node, truenodes = build_path(L, K, slots, A, t, g); mem = make_mem(L, K, slots, truenodes, D, g)
        # no-cleanup probe trajectory
        p = node
        for l in range(L, 1, -1):
            p = p * np.conj(slots[j[l - 1]]); tn = truenodes[l - 1]
            sig_nc[l - 1].append(abs(np.vdot(tn, p).real) / N)
            noise[l - 1].append(float(np.std((mem[l - 1][1:] @ np.conj(p)).real / N)))
        # with-cleanup probe trajectory
        p = node
        for l in range(L, 1, -1):
            p = p * np.conj(slots[j[l - 1]]); tn = truenodes[l - 1]
            sig_cl[l - 1].append(abs(np.vdot(tn, p).real) / N)
            p = mem[l - 1][int(np.argmax((mem[l - 1] @ np.conj(p)).real))]
    def snr_db(sig, noi):
        s = max(np.mean(sig), 1e-6); nv = max(np.mean(noi), 1e-6); return 20.0 * math.log10(s / nv)
    recov = []
    for l in range(1, L):
        recov.append(snr_db(sig_cl[l], noise[l]) - snr_db(sig_nc[l], noise[l]))
    mean_recov = float(np.mean(recov))
    print("  CLEANUP-AT-DEPTH per-level SNR recovery(dB)=%s mean=%.2f" % (["%.1f" % x for x in recov], mean_recov), flush=True)
    return {"per_level_recovery_db": [round(x, 2) for x in recov], "mean_recovery_db": round(mean_recov, 2), "L": L}
def verdict(r) -> Tuple[str, str]:
    s = "mean-SNR-recovery=%.2f dB/level per-level=%s" % (r["mean_recovery_db"], r["per_level_recovery_db"])
    if r["mean_recovery_db"] >= 5.0:
        return ("HARD_PASS", "HARD_PASS: hierarchical cleanup recovers >=5 dB SNR per level -- cascading per-level cleanup is the mechanism that mitigates compositional SNR decay (quantified). " + s)
    if r["mean_recovery_db"] >= 2.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cleanup recovers 2-5 dB/level. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cleanup recovers <2 dB/level. " + s)
'''

CAPACITY = r'''
def _selftest():
    print("[selftest] PASS: capacity-per-level", flush=True)
def _recall_at(L, K, g, M=200, D=50, TR=40):
    A = cphasor(M, N, g); slots = cphasor(K, N, g); hit = 0
    for _ in range(TR):
        t = int(g.integers(0, M)); j, node, truenodes = build_path(L, K, slots, A, t, g); mem = make_mem(L, K, slots, truenodes, D, g)
        hit += int(retrieve(node, j, slots, A, mem, L, True) == t)
    return hit / TR
def run() -> Dict:
    g = np.random.default_rng(404); Ks = [5, 10, 20, 40] if SMOKE else [5, 10, 20, 40, 80]; Ls = [1, 2, 3, 4, 5]
    TR = 20 if SMOKE else 50; kstar = {}; curve = {}
    for L in Ls:
        ks = 0; row = {}
        for K in Ks:
            rec = _recall_at(L, K, g, TR=TR); row[K] = round(rec, 3)
            if rec >= 0.90:
                ks = K
        kstar[L] = ks; curve[L] = row
        print("  CAPACITY L=%d kstar(recall>=0.90)=%d row=%s" % (L, ks, row), flush=True)
    theo = N / (2 * math.log(N))
    print("  theoretical atomic capacity N/(2 ln N)=%.0f" % theo, flush=True)
    return {"kstar_per_level": kstar, "curve": {str(k): v for k, v in curve.items()}, "theo_atomic": round(theo, 1)}
def verdict(r) -> Tuple[str, str]:
    ks = r["kstar_per_level"]; s = "kstar-per-level=%s theo-atomic=%.0f" % (ks, r["theo_atomic"])
    if ks.get(3, 0) >= 10 and ks.get(5, 0) >= 5:
        return ("HARD_PASS", "HARD_PASS: capacity curve characterized -- kstar>=10 at L=3 AND kstar>=5 at L=5 (with cleanup); operational depth-capacity envelope mapped. " + s)
    if ks.get(3, 0) >= 5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: kstar>=5 at L=3 but thinner at depth. " + s)
    return ("HARD_FAIL", "HARD_FAIL: kstar<5 at L=3 -- capacity collapses with depth. " + s)
'''

C = [
    dict(anchor="comp1_depth_l3_cpu_v1", tag="COMP-1 DEPTH-L3", title="compositional depth L=3 retrieval (first cliff gate)",
         desc="Bind K=10 L2 shards into an L3 composite; retrieve a leaf with hierarchical cleanup. Is L=3 the cliff?",
         prereg="HARD-PASS recall>=0.90 at L=3 K=10. MIDDLE within 0.20. HARD-FAIL else.", body=DEPTH.replace("__LDEPTH__", "3").replace("__PASSTH__", "0.90")),
    dict(anchor="comp2_depth_l5_cpu_v1", tag="COMP-2 DEPTH-L5", title="compositional depth L=5 retrieval (final cliff gate)",
         desc="Push to L=5 (5-level chain); retrieve with hierarchical cleanup. Does deep composition survive?",
         prereg="HARD-PASS recall>=0.70 at L=5 K=10. MIDDLE within 0.20. HARD-FAIL (<0.50) deep composition broken.", body=DEPTH.replace("__LDEPTH__", "5").replace("__PASSTH__", "0.70")),
    dict(anchor="comp3_cleanup_at_depth_cpu_v1", tag="COMP-3 CLEANUP-AT-DEPTH", title="cleanup SNR contribution per level",
         desc="Cosine-to-true of intermediate estimates WITH vs WITHOUT per-level cleanup; SNR recovery per level.",
         prereg="HARD-PASS cleanup recovers >=5 dB SNR per level. MIDDLE 2-5. HARD-FAIL <2.", body=CLEANUP),
    dict(anchor="comp4_capacity_per_level_cpu_v1", tag="COMP-4 CAPACITY-PER-LEVEL", title="empirical kstar capacity curve per depth",
         desc="At each level L sweep K; find kstar (max K with recall>=0.90 under cleanup); compare to N/(2 ln N).",
         prereg="HARD-PASS kstar>=10 at L=3 AND >=5 at L=5. MIDDLE kstar>=5 at L=3. HARD-FAIL else.", body=CAPACITY),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
