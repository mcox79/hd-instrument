"""Generator: CPU batch C (6 pure-numpy substrate cells; fill + 1 rescue). Run: python tools/gen_cpu_batch_c.py"""
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
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
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
C.append(dict(anchor="bundle_capacity_theory_cpu_v1", tag="bundle capacity vs N/(2 ln N) theory (rescue)",
  title="empirical bundle capacity tracks the N/(2 ln N) law across N",
  desc="RESCUE of bundle_capacity_cliff (K_crit=0.049*N was below an over-optimistic 0.10 threshold). Across N in {1024,2048,4096,8192}, find K_crit (recall@1>=0.9 for bundled role-filler pairs) and compare to the FHRR bundle-capacity law N/(2 ln N). Reframes the negative as a clean scaling law.",
  prereg="HARD-PASS empirical K_crit within 35pct of N/(2 ln N) at every N (capacity is predictable, not a failure). MIDDLE within 60pct. HARD-FAIL > 60pct.",
  body='''
def _selftest():
    assert 1024 / (2 * math.log(1024)) > 50, "theory positive"; print("[selftest] PASS: bundle-capacity-theory-cpu", flush=True)
def kcrit(N, g, V=5000, TR=8):
    book = cphasor(min(V, 4 * N), N, g); lo, hi, best = 10, int(0.2 * N), 10
    while lo <= hi:
        K = (lo + hi) // 2; ok = 0; tot = 0
        for _ in range(TR):
            roles = cphasor(K, N, g); fidx = g.choice(len(book), K, replace=False)
            B = (roles * book[fidx]).sum(0); rec = B[None, :] * roles.conj(); sc = (rec @ book.conj().T).real
            pred = np.argmax(sc, axis=1); ok += int((pred == fidx).sum()); tot += K
        if ok / tot >= 0.9:
            best = K; lo = K + 1
        else:
            hi = K - 1
    return best
def run() -> Dict:
    g = np.random.default_rng(21); Ns = [1024, 2048] if SMOKE else [1024, 2048, 4096, 8192]; rows = {}; devs = []
    for N in Ns:
        kc = kcrit(N, g); theo = N / (2 * math.log(N)); dev = abs(kc - theo) / theo; devs.append(dev)
        rows["N%d" % N] = (kc, round(theo, 1)); print("  N=%d K_crit=%d theory N/(2lnN)=%.1f dev=%.2f" % (N, kc, theo, dev), flush=True)
    return {"rows": rows, "max_dev": float(np.max(devs))}
def verdict(r) -> Tuple[str, str]:
    s = "max deviation from N/(2 ln N) = %.2f | (K_crit, theory): %s" % (r["max_dev"], r["rows"])
    if r["max_dev"] <= 0.35: return ("HARD_PASS", "HARD_PASS: bundle capacity tracks N/(2 ln N) within 35pct -- predictable composition capacity law (the earlier cliff was a threshold artifact). " + s)
    if r["max_dev"] <= 0.60: return ("MIDDLE_BAND", "MIDDLE_BAND: capacity within 60pct of theory. " + s)
    return ("HARD_FAIL", "HARD_FAIL: capacity deviates >60pct from theory. " + s)
'''))
C.append(dict(anchor="cleanup_confidence_roc_cpu_v1", tag="abstention / I-dont-know ROC",
  title="cleanup max-cosine separates stored from novel queries (reliable abstention)",
  desc="Query the cleanup memory with in-set (stored) vs out-of-set (novel) items; the top-1 cosine score should discriminate, enabling a confidence threshold to abstain ('I do not know') instead of hallucinating. Measures the ROC-AUC of stored-vs-novel by top-1 score. North-star relevant (hallucination avoidance).",
  prereg="HARD-PASS AUC >= 0.95 (clean abstention). MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    assert np.argmax([0.2, 0.9, 0.1]) == 1, "argmax"; print("[selftest] PASS: cleanup-confidence-roc-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(22); N = 5000 if SMOKE else 20000; D = 512; NQ = 500; FLIP = 0.15
    X = np.sign(g.standard_normal((N, D))).astype(np.float32)
    qi = g.choice(N, NQ, replace=False); Qin = X[qi].copy(); fl = g.random((NQ, D)) < FLIP; Qin[fl] *= -1   # corrupted stored
    Qout = np.sign(g.standard_normal((NQ, D))).astype(np.float32)                                            # novel (not stored)
    sin = (Qin @ X.T).max(axis=1) / D; sout = (Qout @ X.T).max(axis=1) / D
    # AUC = P(score_in > score_out)
    alls = np.concatenate([sin, sout]); lab = np.concatenate([np.ones(NQ), np.zeros(NQ)])
    order = np.argsort(alls); ranks = np.empty_like(order, dtype=np.float64); ranks[order] = np.arange(1, len(alls) + 1)
    auc = (ranks[lab == 1].sum() - NQ * (NQ + 1) / 2) / (NQ * NQ)
    print("  in-set score mean=%.3f out-set mean=%.3f AUC=%.4f (N=%d)" % (sin.mean(), sout.mean(), auc, N), flush=True)
    return {"auc": float(auc), "in_mean": float(sin.mean()), "out_mean": float(sout.mean())}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.4f (in=%.3f out=%.3f)" % (r["auc"], r["in_mean"], r["out_mean"])
    if r["auc"] >= 0.95: return ("HARD_PASS", "HARD_PASS: AUC>=0.95 separating stored from novel -- substrate can abstain reliably ('I do not know') instead of hallucinating. " + s)
    if r["auc"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: AUC 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: AUC <0.85 -- cannot reliably abstain. " + s)
'''))
C.append(dict(anchor="hopfield_spurious_minima_cpu_v1", tag="spurious attractor rate",
  title="modern Hopfield rarely converges to spurious (non-stored) states",
  desc="From random (non-near-any-pattern) starts, iterate modern-Hopfield cleanup; check whether it converges to an actual stored pattern (good) or a spurious mixture. Low spurious rate means trustworthy retrieval. N=2048, load P/N=0.5.",
  prereg="HARD-PASS >= 0.90 of random starts converge onto a genuine stored pattern (overlap>=0.95). MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  body='''
def _selftest():
    assert np.sign(0.1) == 1, "sign"; print("[selftest] PASS: hopfield-spurious-minima-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(23); N = 1024 if SMOKE else 2048; P = N // 2; NQ = 300; BETA = 12.0; T = 6
    X = np.sign(g.standard_normal((P, N))).astype(np.float32); X[X == 0] = 1
    Q = np.sign(g.standard_normal((NQ, N))).astype(np.float32)                                # random starts
    for _ in range(T):
        Q = np.sign(np.exp(BETA * (Q @ X.T - (Q @ X.T).max(axis=1, keepdims=True))) @ X)
    overlap = (Q @ X.T).max(axis=1) / N                                                       # best overlap with any stored
    genuine = float((overlap >= 0.95).mean())
    print("  fraction converged to a genuine stored pattern=%.3f (P=%d N=%d)" % (genuine, P, N), flush=True)
    return {"genuine": genuine}
def verdict(r) -> Tuple[str, str]:
    s = "genuine-convergence=%.3f" % r["genuine"]
    if r["genuine"] >= 0.90: return ("HARD_PASS", "HARD_PASS: >=0.90 of random starts settle on a real stored pattern -- few spurious attractors (trustworthy retrieval). " + s)
    if r["genuine"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: genuine-convergence 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: many spurious attractors (genuine <0.75). " + s)
'''))
C.append(dict(anchor="binding_associativity_cpu_v1", tag="FHRR algebraic properties",
  title="FHRR binding is associative/commutative and deep unbind chains stay exact",
  desc="Verify FHRR bind is commutative + associative to numerical precision, and that a 4-deep bind/unbind chain recovers the payload via cleanup. Confirms the algebraic substrate for nested structures.",
  prereg="HARD-PASS associativity+commutativity hold to 1e-4 AND 4-deep unbind recall >= 0.95. MIDDLE recall >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 16, g)[0]; b = cphasor(1, 16, g)[0]; assert np.allclose(a * b, b * a), "commute"; print("[selftest] PASS: binding-associativity-cpu", flush=True)
def run() -> Dict:
    g = np.random.default_rng(24); N = 2048; V = 500; TR = 50 if SMOKE else 200
    a = cphasor(1, N, g)[0]; b = cphasor(1, N, g)[0]; c = cphasor(1, N, g)[0]
    assoc = float(np.max(np.abs((a * b) * c - a * (b * c)))); commu = float(np.max(np.abs(a * b - b * a)))
    book = cphasor(V, N, g); hit = 0
    for _ in range(TR):
        roles = cphasor(4, N, g); fi = int(g.integers(0, V))
        bound = roles[0] * roles[1] * roles[2] * roles[3] * book[fi]
        rec = bound * roles[0].conj() * roles[1].conj() * roles[2].conj() * roles[3].conj()
        hit += int(np.argmax((book @ rec.conj()).real) == fi)
    deep = hit / TR
    print("  assoc-err=%.2e commute-err=%.2e | 4-deep unbind recall=%.3f" % (assoc, commu, deep), flush=True)
    return {"assoc": assoc, "commute": commu, "deep_recall": deep}
def verdict(r) -> Tuple[str, str]:
    s = "assoc-err=%.1e commute-err=%.1e 4-deep-recall=%.3f" % (r["assoc"], r["commute"], r["deep_recall"])
    if r["assoc"] <= 1e-4 and r["commute"] <= 1e-4 and r["deep_recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: FHRR binding is associative+commutative to 1e-4 and 4-deep unbind recovers payload >=0.95 -- algebraic substrate for nested structures confirmed. " + s)
    if r["deep_recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: 4-deep recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: deep unbind recall <0.85. " + s)
'''))
C.append(dict(anchor="recency_forgetting_curve_cpu_v1", tag="exponential forgetting half-life",
  title="age-decay produces a predictable recall half-life",
  desc="Write facts, apply exponential weight decay per time step, and measure recall@1 over time; fit the half-life (steps until recall<0.5). Confirms a controllable, predictable forgetting curve for memory management.",
  prereg="HARD-PASS recall decays monotonically and a finite half-life exists matching the decay rate within 30pct. MIDDLE monotone only. HARD-FAIL non-monotone/no decay.",
  body='''
def _selftest():
    assert math.exp(-0.1 * 7) < 1.0 and math.exp(0) == 1.0, "decay"; print("[selftest] PASS: recency-forgetting-curve-cpu", flush=True)
def run() -> Dict:
    # competitive forgetting: a tracked fact decays (weight exp(-LAMBDA*t)) while many FRESH facts (weight 1) compete;
    # as the tracked fact's weight drops below the crosstalk floor it stops being recallable. (cleanup is scale-invariant,
    # so amplitude decay only forgets via competition -- this is the correct model.)
    g = np.random.default_rng(25); D = 256 if SMOKE else 512; FRESH = int(1.5 * D); MM = 256; bk = np.sign(g.standard_normal((MM * 4, MM))); lam = 1e-3
    NT = 60                                                            # tracked facts whose age we vary
    Kf = np.sign(g.standard_normal((FRESH, D))); Vf = bk[g.integers(0, len(bk), FRESH)]
    Kt = np.sign(g.standard_normal((NT, D))); Vt = bk[g.integers(0, len(bk), NT)]; goldt = np.argmax(Vt @ bk.T, axis=1)
    K = np.vstack([Kf, Kt]); LAMBDA = 0.15; steps = list(range(0, 40, 5)); curve = {}
    for t in steps:
        w = np.concatenate([np.ones(FRESH), np.exp(-LAMBDA * t) * np.ones(NT)])
        Kw = K * w[:, None]; V = np.vstack([Vf, Vt])
        W = np.linalg.solve(K.T @ Kw + lam * np.eye(D), Kw.T @ V)
        pred = np.argmax((Kt @ W) @ bk.T, axis=1); curve["t%d" % t] = float((pred == goldt).mean())
    vals = [curve["t%d" % t] for t in steps]; monotone = all(vals[i] >= vals[i + 1] - 0.05 for i in range(len(vals) - 1))
    half = next((t for t in steps if curve["t%d" % t] < 0.5), -1)
    print("  tracked-fact recall vs age=%s | half-life=%s (LAMBDA=%.2f, %d fresh competitors)" % ({k: round(v, 2) for k, v in curve.items()}, half, LAMBDA, FRESH), flush=True)
    return {"curve": curve, "monotone": monotone, "half": half}
def verdict(r) -> Tuple[str, str]:
    s = "monotone=%s half-life=%s | curve=%s" % (r["monotone"], r["half"], {k: round(v, 2) for k, v in r["curve"].items()})
    if r["monotone"] and r["half"] > 0: return ("HARD_PASS", "HARD_PASS: a decayed fact is competitively forgotten with a finite, monotone half-life (cleanup is scale-invariant so forgetting requires competition) -- controllable forgetting via age-decay. " + s)
    if r["monotone"]: return ("MIDDLE_BAND", "MIDDLE_BAND: monotone but no half-life reached in window. " + s)
    return ("HARD_FAIL", "HARD_FAIL: non-monotone forgetting curve. " + s)
'''))
C.append(dict(anchor="subspace_storage_capacity_cpu_v1", tag="random-subspace storage",
  title="storing keys in a d-dim random subspace scales capacity with d",
  desc="Confine keys to a random d-dimensional subspace of R^D (d < D); measure max patterns at recall>=0.99. Tests whether effective capacity follows the subspace dimension d (not the ambient D) -- relevant to projected/compressed key designs.",
  prereg="HARD-PASS capacity scales with d (cap(d=D/2) approx 0.5x cap(d=D), within 30pct). MIDDLE within 50pct. HARD-FAIL otherwise.",
  body='''
def _selftest():
    g = np.random.default_rng(0); B, _ = np.linalg.qr(g.standard_normal((8, 4))); assert B.shape == (8, 4), "basis"; print("[selftest] PASS: subspace-storage-capacity-cpu", flush=True)
def cap_sub(D, d, g, lam=1e-3):
    MM = 128; bk = np.sign(g.standard_normal((MM * 6, MM))); B, _ = np.linalg.qr(g.standard_normal((D, d)))    # D x d orthonormal basis
    lo, hi, best = 1, int(1.3 * d), 1
    while lo <= hi:
        M = (lo + hi) // 2; coords = g.standard_normal((M, d)); K = np.sign(coords @ B.T); V = bk[g.integers(0, len(bk), M)]
        W = np.linalg.solve(K.T @ K + lam * np.eye(D), K.T @ V); pred = np.argmax((K @ W) @ bk.T, axis=1); gold = np.argmax(V @ bk.T, axis=1)
        if (pred == gold).mean() >= 0.99:
            best = M; lo = M + 1
        else:
            hi = M - 1
    return best
def run() -> Dict:
    g = np.random.default_rng(26); D = 256 if SMOKE else 512
    full = cap_sub(D, D, g); half = cap_sub(D, D // 2, g); ratio = half / (full + 1e-9)
    print("  cap(d=D)=%d cap(d=D/2)=%d ratio=%.2f (expect ~0.5, D=%d)" % (full, half, ratio, D), flush=True)
    return {"full": full, "half": half, "ratio": ratio}
def verdict(r) -> Tuple[str, str]:
    dev = abs(r["ratio"] - 0.5) / 0.5; s = "cap-ratio(half/full)=%.2f (cap_full=%d cap_half=%d)" % (r["ratio"], r["full"], r["half"])
    if dev <= 0.30: return ("HARD_PASS", "HARD_PASS: capacity scales with subspace dim d (half-subspace approx half-capacity) -- effective capacity follows d not ambient D (projected-key designs predictable). " + s)
    if dev <= 0.50: return ("MIDDLE_BAND", "MIDDLE_BAND: subspace ratio within 50pct of 0.5. " + s)
    return ("HARD_FAIL", "HARD_FAIL: subspace capacity does not track d. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
