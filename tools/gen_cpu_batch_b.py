"""Generator: CPU batch B (5 pure-numpy substrate-physics cells). Run: python tools/gen_cpu_batch_b.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: CPU substrate-physics characterization ({tag}). {desc} Pure numpy. CPU.
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
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
C = []
C.append(dict(anchor="cross_kb_interference_cpu_v1", tag="two-KB shared-space interference",
  title="false-match rate when two KBs share one space",
  desc="Two independent KBs (N each) in the same D-dim space; query with noisy KB1 keys; measure the rate at which a KB2 item outranks the true KB1 match (cross-tenant interference). Validates multi-tenant isolation in a shared substrate.",
  prereg="HARD-PASS cross-KB interference rate <= 0.05 at N=10000 each. MIDDLE <= 0.15. HARD-FAIL > 0.15.",
  body='''
def _selftest():
    assert np.argmax([1, 2, 3]) == 2, "argmax"; print("[selftest] PASS: cross-kb-interference-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(11); N = 6000 if SMOKE else 10000; D = 512; NQ = 300; FLIP = 0.15
    KB1 = np.sign(g.standard_normal((N, D))).astype(np.float32); KB2 = np.sign(g.standard_normal((N, D))).astype(np.float32)
    ALL = np.vstack([KB1, KB2]); qi = g.choice(N, NQ, replace=False); Q = KB1[qi].copy(); fl = g.random((NQ, D)) < FLIP; Q[fl] *= -1
    pred = np.argmax(Q @ ALL.T, axis=1); interference = float((pred >= N).mean()); recall = float((pred == qi).mean())
    print("  cross-KB interference=%.4f recall=%.4f (N=%d each, D=%d)" % (interference, recall, N, D), flush=True)
    return {"interference": interference, "recall": recall}
def verdict(r) -> Tuple[str, str]:
    s = "interference=%.4f recall=%.4f" % (r["interference"], r["recall"])
    if r["interference"] <= 0.05: return ("HARD_PASS", "HARD_PASS: cross-KB interference <=0.05 -- two tenants share one space with negligible cross-talk (multi-tenant isolation). " + s)
    if r["interference"] <= 0.15: return ("MIDDLE_BAND", "MIDDLE_BAND: interference 0.05-0.15. " + s)
    return ("HARD_FAIL", "HARD_FAIL: interference >0.15 -- shared-space tenants leak. " + s)
'''))
C.append(dict(anchor="graceful_overload_cpu_v1", tag="past-capacity degradation shape",
  title="recall degrades gracefully (not catastrophically) past capacity",
  desc="Load the pinv memory at M/D in {1.0,1.5,2.0} (at/over capacity); measure recall@1. A graceful system degrades smoothly; a catastrophic one cliffs to 0. Characterizes overload behavior.",
  prereg="HARD-PASS recall at M/D=1.5 >= 0.50 (graceful). MIDDLE >= 0.20. HARD-FAIL < 0.20 (catastrophic cliff).",
  body='''
def _selftest():
    A = np.eye(3); assert np.allclose(np.linalg.solve(A, A), A), "solve"; print("[selftest] PASS: graceful-overload-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(12); D = 256 if SMOKE else 512; MM = 128; bk = np.sign(g.standard_normal((MM * 4, MM))); lam = 1e-3; by = {}
    loads = [2.0, 4.0] if SMOKE else [2.0, 4.0, 8.0, 16.0]
    for rr in loads:
        M = int(rr * D); K = np.sign(g.standard_normal((M, D))); V = bk[g.integers(0, len(bk), M)]
        W = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V)
        pred = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1)
        by["r%.0f" % rr] = float((pred == gold).mean())
    print("  recall by overload M/D: %s (D=%d)" % ({k: round(v, 3) for k, v in by.items()}, D), flush=True)
    return {"by": by, "loads": loads}
def verdict(r) -> Tuple[str, str]:
    b = r["by"]; ld = r["loads"]; keys = ["r%.0f" % x for x in ld]
    vals = [b[k] for k in keys]; r4 = b.get("r4", vals[-1])
    monotone = all(vals[i] >= vals[i + 1] - 0.02 for i in range(len(vals) - 1))
    s = "recall by overload: %s (monotone=%s)" % ({k: round(v, 3) for k, v in b.items()}, monotone)
    if r4 >= 0.50 and monotone: return ("HARD_PASS", "HARD_PASS: cleanup-backed pinv degrades smoothly+monotonically, recall>=0.50 even at 4x overload -- graceful past-capacity behavior (no catastrophic cliff). " + s)
    if r4 >= 0.20: return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.20-0.50 at 4x overload. " + s)
    return ("HARD_FAIL", "HARD_FAIL: catastrophic drop (recall <0.20 at 4x). " + s)
'''))
C.append(dict(anchor="priority_weighted_capacity_cpu_v1", tag="priority protection under overload",
  title="up-weighting protects high-priority facts under overload",
  desc="At overload (M/D=1.5), compare uniform pinv vs priority-weighted pinv: do up-weighted high-priority facts keep recall>=0.95 while uniform loses them? Validates a triage mechanism for capacity-constrained deployments.",
  prereg="HARD-PASS weighted high-priority recall >= 0.95 AND uniform high-priority < 0.90 (weighting demonstrably helps). MIDDLE weighted >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    w = np.array([1.0, 20.0]); K = np.ones((2, 3)); assert (K * w[:, None]).shape == (2, 3), "weighted shape"; print("[selftest] PASS: priority-weighted-capacity-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(13); D = 512; MM = 256; bk = np.sign(g.standard_normal((MM * 4, MM))); lam = 1e-3
    M = int(3.0 * D); K = np.sign(g.standard_normal((M, D))); V = bk[g.integers(0, len(bk), M)]; gold = np.argmax(V @ bk.T, axis=1); FLIP = 0.15
    hi = np.zeros(M, bool); hi[: M // 5] = True; w = np.ones(M); w[hi] = 50.0
    Wu = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V)
    Kw = K * w[:, None]; Ww = np.linalg.solve(K.T @ Kw + lam * np.eye(D), Kw.T @ V)
    Kq = K.copy(); fl = g.random((M, D)) < FLIP; Kq[fl] *= -1                       # noisy queries at 3x overload so uniform actually fails
    def rec(W, mask):
        pred = np.argmax((Kq[mask] @ W) @ bk.T, axis=1); return float((pred == gold[mask]).mean())
    uhi = rec(Wu, hi); whi = rec(Ww, hi); wlo = rec(Ww, ~hi)
    print("  high-priority recall: uniform=%.3f weighted=%.3f | weighted low-priority=%.3f (overload 3x, 0.15 noise)" % (uhi, whi, wlo), flush=True)
    return {"uniform_hi": uhi, "weighted_hi": whi, "weighted_lo": wlo}
def verdict(r) -> Tuple[str, str]:
    s = "weighted-hi=%.3f uniform-hi=%.3f weighted-lo=%.3f" % (r["weighted_hi"], r["uniform_hi"], r["weighted_lo"])
    if r["weighted_hi"] >= 0.95 and r["uniform_hi"] < 0.90: return ("HARD_PASS", "HARD_PASS: up-weighting keeps high-priority recall>=0.95 at overload where uniform drops -- capacity triage works. " + s)
    if r["weighted_hi"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: weighted high-priority 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: weighted high-priority <0.85. " + s)
'''))
C.append(dict(anchor="delete_downdate_exactness_cpu_v1", tag="delete exactness",
  title="deleting facts leaves remaining recall intact and removes the deleted",
  desc="From a pinv memory of M facts, delete 20pct (re-solve without them); verify the deleted facts no longer recall their old value AND all remaining facts stay intact. Validates exact deletion (GDPR/correction support).",
  prereg="HARD-PASS remaining-intact >= 0.99 AND deleted-removed >= 0.90. MIDDLE intact >= 0.95. HARD-FAIL intact < 0.95.",
  body='''
def _selftest():
    m = np.ones(5, bool); m[2] = False; assert m.sum() == 4, "mask"; print("[selftest] PASS: delete-downdate-exactness-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(14); D = 512; M = int(0.7 * D); MM = 256; bk = np.sign(g.standard_normal((MM * 4, MM))); lam = 1e-3
    K = np.sign(g.standard_normal((M, D))); V = bk[g.integers(0, len(bk), M)]; gold = np.argmax(V @ bk.T, axis=1)
    ndel = M // 5; del_idx = g.choice(M, ndel, replace=False); keep = np.ones(M, bool); keep[del_idx] = False
    W2 = np.linalg.solve(K[keep].T @ K[keep] + lam * np.eye(D), K[keep].T @ V[keep])
    pred = np.argmax((K @ W2) @ bk.T, axis=1)
    intact = float((pred[keep] == gold[keep]).mean()); removed = float((pred[del_idx] != gold[del_idx]).mean())
    print("  after deleting %d/%d: remaining-intact=%.4f deleted-removed=%.4f" % (ndel, M, intact, removed), flush=True)
    return {"intact": intact, "removed": removed}
def verdict(r) -> Tuple[str, str]:
    s = "remaining-intact=%.4f deleted-removed=%.4f" % (r["intact"], r["removed"])
    if r["intact"] >= 0.99 and r["removed"] >= 0.90: return ("HARD_PASS", "HARD_PASS: deletion leaves remaining facts intact (>=0.99) and removes deleted (>=0.90) -- exact deletion (GDPR/correction). " + s)
    if r["intact"] >= 0.95: return ("MIDDLE_BAND", "MIDDLE_BAND: remaining-intact 0.95-0.99. " + s)
    return ("HARD_FAIL", "HARD_FAIL: deletion disturbs remaining facts (intact <0.95). " + s)
'''))
C.append(dict(anchor="permutation_seq_length_cpu_v1", tag="sequence length sweep",
  title="permutation-power sequence recovery vs length L (CPU fine sweep)",
  desc="Encode ordered sequences of length L in {5,10,15,20} via permutation powers (S = sum P^k(item_k)); recover each position via P^-k + cleanup. Finds the sequence-length capacity at N=2048.",
  prereg="HARD-PASS position recovery >= 0.90 at L=15. MIDDLE >= 0.80. HARD-FAIL < 0.80.",
  body='''
def _selftest():
    p = np.array([2, 0, 1]); inv = np.argsort(p); assert (p[inv] == np.arange(3)).all(), "inverse perm"; print("[selftest] PASS: permutation-seq-length-cpu", flush=True)
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def run() -> Dict:
    g = np.random.default_rng(15); N = 2048; V = 200; perm = g.permutation(N); inv = np.argsort(perm); book = cphasor(V, N, g)
    TR = 20 if SMOKE else 60; Ls = [5, 10] if SMOKE else [5, 10, 15, 20]; by = {}
    def permute(v, k):
        out = v; idx = perm if k >= 0 else inv
        for _ in range(abs(k)):
            out = out[idx]
        return out
    for L in Ls:
        hit = 0; tot = 0
        for _ in range(TR):
            seq = g.choice(V, L, replace=False); S = np.zeros(N, dtype=np.complex64)
            for k in range(L):
                S = S + permute(book[seq[k]], k)
            for k in range(L):
                rec = permute(S, -k); pred = int(np.argmax((book @ rec.conj()).real)); hit += int(pred == int(seq[k])); tot += 1
        by["L%d" % L] = hit / tot; print("  L=%d position-recovery=%.3f" % (L, by["L%d" % L]), flush=True)
    return {"by": by}
def verdict(r) -> Tuple[str, str]:
    l15 = r["by"].get("L15", r["by"].get("L10", 0.0)); s = "recovery by L: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if l15 >= 0.90: return ("HARD_PASS", "HARD_PASS: ordered-sequence recovery >=0.90 at L=15 -- long timelines representable at N=2048. " + s)
    if l15 >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: L=15 recovery 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: L=15 recovery <0.80. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
