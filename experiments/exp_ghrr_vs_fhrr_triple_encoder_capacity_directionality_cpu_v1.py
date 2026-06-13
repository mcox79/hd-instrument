"""
exp_ghrr_vs_fhrr_triple_encoder_capacity_directionality_cpu_v1.py -- INGEST encoder probe: GHRR (non-commutative) vs FHRR (current production) -- CPU/local (no heat, synthetic, no atom reads -> no write-race).

ROUTING: Research handoff ANCHOR 6 (Drill 1) -- "triple-to-VSA encoder upgrade probe." Before pouring 4.37M external facts onto the
  substrate, RULE IN/OUT the GHRR upgrade (ArXiv 2405.09689, generalized/matrix-valued HRR with NON-COMMUTATIVE binding) over the current
  production FHRR two-vector composite (PP-410, alpha=0.5, COMMUTATIVE circular-convolution binding). Relational triples are DIRECTIONAL
  (s-pred-o; "a depends_on b" != "b depends_on a"); commutative binding cannot natively distinguish argument order, GHRR can. This is a
  cheap, self-contained, decisive probe: synthetic codebook + synthetic triples; NO substrate atom reads (so NO desktop atom-write race);
  numpy only (no torch/GPU); negligible heat.

  DESIGN (exp_dev owns; matched real-parameter budget for fairness):
   - FHRR atom = unit-modulus complex phasor vector dim Nf (2*Nf reals). bind = elementwise complex multiply (COMMUTATIVE);
     unbind = multiply by conjugate; superpose = sum; cleanup = max real-cosine over codebook.
   - GHRR atom = B blocks of dxd complex UNITARY matrices (2*B*d*d reals). bind = blockwise matmul (NON-COMMUTATIVE);
     unbind = blockwise matmul by conjugate-transpose (unitary inverse); superpose = sum of block-matrices; cleanup = max Frobenius cosine.
   - Budget match: Nf = B*d*d (so both use the same real-parameter count; here d=4, B=64 -> Nf=1024 ~ substrate 1024-d).
   - CAPACITY: one trace superposing F (role_i, filler_i) bindings; recover each filler by unbinding its role; recall@10 vs codebook.
     Sweep F; BREAK = largest F with mean recall@10 >= 0.5. (The substrate FHRR two-vector empirical break was ~242 atoms.)
   - DIRECTIONALITY: cos(bind(a,b), bind(b,a)) -- FHRR commutative -> ~1.0 (cannot distinguish order); GHRR -> low (distinguishes).

PRE-REGISTERED (Research Drill 1): HARD-PASS GHRR cleanup recall@10 >= FHRR + 0.05 (at the comparison load) AND GHRR capacity-break
  >= 320 (extends beyond the ~242 FHRR regime) -> GHRR upgrade WARRANTED, plan it. MIDDLE exactly one of the two holds. HARD-FAIL GHRR
  not better on EITHER (recall delta < 0.05 AND break < 320) -> rule OUT the upgrade; keep production FHRR PP-410 before ingest.
  (Directionality is a reported secondary structural metric, not a gate.) UNKNOWN on impl/availability error.
ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "ghrr_vs_fhrr_triple_encoder_capacity_directionality_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
D_BLOCK = 4; N_BLOCKS = 64; NF = D_BLOCK * D_BLOCK * N_BLOCKS   # 1024 matched real-parameter budget
M_CODEBOOK = 1000; K_RECALL = 10; CMP_LOAD = 200                 # comparison load for recall@10 delta
F_SWEEP = [50, 100, 200, 320, 500, 800] if not SMOKE else [50, 200]
SEED = 1028


# ---------- FHRR (phasor, commutative) ----------
def fhrr_codebook(M: int, Nf: int, rng) -> np.ndarray:
    ph = rng.uniform(-np.pi, np.pi, size=(M, Nf)); return np.exp(1j * ph)


def fhrr_bind(a, b): return a * b                       # elementwise complex multiply (commutative)
def fhrr_unbind(role, trace): return np.conj(role) * trace


def fhrr_cleanup_topk(qhat, codebook, k):
    # real-cosine of unit-modulus phasors: real(<q, conj(c)>)/Nf
    sims = np.real(codebook @ np.conj(qhat)) / qhat.shape[0]
    return np.argsort(-sims)[:k]


# ---------- GHRR (block unitary matrices, non-commutative) ----------
def _rand_unitary(d, rng):
    X = (rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))) / np.sqrt(2.0)
    Q, R = np.linalg.qr(X); Q = Q * (np.diag(R) / np.abs(np.diag(R)))   # fix phase -> Haar unitary
    return Q


def ghrr_codebook(M, B, d, rng):
    return np.stack([np.stack([_rand_unitary(d, rng) for _ in range(B)]) for _ in range(M)])  # (M,B,d,d)


def ghrr_bind(a, b): return a @ b                       # blockwise matmul (non-commutative)
def ghrr_unbind(role, trace): return np.conj(np.transpose(role, (0, 2, 1))) @ trace  # role^H @ trace


def _frob_cos(A, Bset):
    # Frobenius cosine between trace-block-stack A (B,d,d) and each codebook entry in Bset (M,B,d,d)
    num = np.real(np.einsum("bij,mbij->m", np.conj(A), Bset))
    na = np.sqrt(np.real(np.einsum("bij,bij->", np.conj(A), A)))
    nb = np.sqrt(np.real(np.einsum("mbij,mbij->m", np.conj(Bset), Bset)))
    return num / (na * nb + 1e-12)


def ghrr_cleanup_topk(qhat, codebook, k):
    return np.argsort(-_frob_cos(qhat, codebook))[:k]


# ---------- shared capacity experiment ----------
def capacity_recall(kind: str, F: int, cb, rng) -> float:
    M = cb.shape[0]
    role_idx = rng.choice(M, F, replace=False); fill_idx = rng.choice(M, F, replace=False)
    if kind == "fhrr":
        trace = np.zeros(NF, dtype=complex)
        for i in range(F): trace = trace + fhrr_bind(cb[role_idx[i]], cb[fill_idx[i]])
        hit = 0
        for i in range(F):
            qhat = fhrr_unbind(cb[role_idx[i]], trace)
            if fill_idx[i] in fhrr_cleanup_topk(qhat, cb, K_RECALL): hit += 1
        return hit / F
    else:
        trace = np.zeros((N_BLOCKS, D_BLOCK, D_BLOCK), dtype=complex)
        for i in range(F): trace = trace + ghrr_bind(cb[role_idx[i]], cb[fill_idx[i]])
        hit = 0
        for i in range(F):
            qhat = ghrr_unbind(cb[role_idx[i]], trace)
            if fill_idx[i] in ghrr_cleanup_topk(qhat, cb, K_RECALL): hit += 1
        return hit / F


def directionality(kind: str, cb, rng) -> float:
    M = cb.shape[0]; idx = rng.choice(M, (50, 2), replace=True)
    cs = []
    for a, b in idx:
        if a == b: continue
        if kind == "fhrr":
            ab = fhrr_bind(cb[a], cb[b]); ba = fhrr_bind(cb[b], cb[a])
            cs.append(np.real(np.vdot(ab, ba)) / (np.linalg.norm(ab) * np.linalg.norm(ba) + 1e-12))
        else:
            ab = ghrr_bind(cb[a], cb[b]); ba = ghrr_bind(cb[b], cb[a])
            cs.append(_frob_cos(ab, ba[None])[0])
    return float(np.mean(cs))


def _selftest():
    rng = np.random.RandomState(0)
    U = _rand_unitary(4, rng)
    assert np.allclose(U @ np.conj(U.T), np.eye(4), atol=1e-8), "unitary inverse"
    # GHRR unbind recovers a single binding exactly (no superposition noise)
    cb = ghrr_codebook(3, 2, 4, rng)
    tr = ghrr_bind(cb[0], cb[1])
    rec = ghrr_unbind(cb[0], tr)
    assert _frob_cos(rec, cb[1][None])[0] > 0.999, "ghrr exact unbind"
    # FHRR exact single unbind
    f = fhrr_codebook(3, 32, rng); t = fhrr_bind(f[0], f[1]); r = fhrr_unbind(f[0], t)
    assert np.real(np.vdot(r, f[1])) / 32 > 0.999          # <a,b>=sum(conj(a)*b); r==f[1] -> ==Nf
    assert 1 in fhrr_cleanup_topk(r, f, 1)                 # cleanup recovers the exact filler f[1] (idx 1)
    # directionality: GHRR non-commutative (low), FHRR commutative (==1)
    assert directionality("fhrr", f, np.random.RandomState(1)) > 0.999
    assert directionality("ghrr", cb, np.random.RandomState(1)) < 0.6
    print("[selftest] PASS: ghrr_vs_fhrr_triple_encoder (unitary inverse + exact unbind + commutativity contrast)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _break_point(recall_by_F: Dict[int, float]) -> int:
    ok = [F for F in sorted(recall_by_F) if recall_by_F[F] >= 0.5]
    return max(ok) if ok else 0


def run() -> Dict:
    rng = np.random.RandomState(SEED)
    M = M_CODEBOOK if not SMOKE else 300
    fcb = fhrr_codebook(M, NF, rng)
    gcb = ghrr_codebook(M, N_BLOCKS, D_BLOCK, rng)
    res = {"fhrr": {"recall_by_F": {}}, "ghrr": {"recall_by_F": {}}}
    for kind, cb in (("fhrr", fcb), ("ghrr", gcb)):
        for F in F_SWEEP:
            if F > M: continue
            res[kind]["recall_by_F"][F] = round(capacity_recall(kind, F, cb, rng), 4)
        res[kind]["break"] = _break_point(res[kind]["recall_by_F"])
        res[kind]["directionality_cos"] = round(directionality(kind, cb, rng), 4)
    # comparison-load recall@10
    cl = CMP_LOAD if CMP_LOAD <= M else M // 2
    f_at = res["fhrr"]["recall_by_F"].get(cl) or round(capacity_recall("fhrr", cl, fcb, rng), 4)
    g_at = res["ghrr"]["recall_by_F"].get(cl) or round(capacity_recall("ghrr", cl, gcb, rng), 4)
    delta = round(g_at - f_at, 4)
    print("  budget: Nf=%d  B=%d d=%d (reals: FHRR=%d GHRR=%d)" % (NF, N_BLOCKS, D_BLOCK, 2 * NF, 2 * N_BLOCKS * D_BLOCK * D_BLOCK), flush=True)
    print("  FHRR recall@10 by F: %s  break=%d  dir-cos=%.3f" % (res["fhrr"]["recall_by_F"], res["fhrr"]["break"], res["fhrr"]["directionality_cos"]), flush=True)
    print("  GHRR recall@10 by F: %s  break=%d  dir-cos=%.3f" % (res["ghrr"]["recall_by_F"], res["ghrr"]["break"], res["ghrr"]["directionality_cos"]), flush=True)
    print("  recall@10 at load F=%d: FHRR=%.4f GHRR=%.4f  delta=%+.4f" % (cl, f_at, g_at, delta), flush=True)
    return {"cmp_load": cl, "fhrr_recall_at_load": f_at, "ghrr_recall_at_load": g_at, "recall_delta": delta,
            "fhrr_break": res["fhrr"]["break"], "ghrr_break": res["ghrr"]["break"],
            "fhrr_dir_cos": res["fhrr"]["directionality_cos"], "ghrr_dir_cos": res["ghrr"]["directionality_cos"],
            "fhrr_recall_by_F": res["fhrr"]["recall_by_F"], "ghrr_recall_by_F": res["ghrr"]["recall_by_F"], "Nf": NF}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + str(r["error"]))
    d = r["recall_delta"]; gb = r["ghrr_break"]
    recall_win = d >= 0.05; break_win = gb >= 320
    s = ("matched-budget Nf=%d; recall@10 at load F=%d: FHRR=%.4f GHRR=%.4f (delta=%+.4f, need>=+0.05); capacity-break FHRR=%d GHRR=%d "
         "(need GHRR>=320); directionality cos FHRR=%.3f (commutative -> cannot distinguish a-R-b from b-R-a) GHRR=%.3f (non-commutative -> distinguishes)") % (
        r["Nf"], r["cmp_load"], r["fhrr_recall_at_load"], r["ghrr_recall_at_load"], d, r["fhrr_break"], gb, r["fhrr_dir_cos"], r["ghrr_dir_cos"])
    if recall_win and break_win:
        return ("HARD_PASS", "HARD_PASS: GHRR beats FHRR on BOTH cleanup recall@10 (delta=%+.4f) AND capacity-break (%d>=320) at matched parameter budget -- the non-commutative upgrade is WARRANTED; plan GHRR before the 4.37M-fact ingest. " % (d, gb) + s)
    if recall_win or break_win:
        return ("MIDDLE_BAND", "MIDDLE_BAND: GHRR wins on exactly one axis (recall_win=%s, break_win=%s) -- partial upgrade case; non-commutative directionality is a real structural gain but capacity/recall parity is mixed. Decide per ingest priority. " % (recall_win, break_win) + s)
    return ("HARD_FAIL", "HARD_FAIL: GHRR does NOT beat FHRR on recall (delta=%+.4f<0.05) OR capacity (break=%d<320) at matched budget -- rule OUT the GHRR upgrade for capacity/recall; keep production FHRR PP-410. (GHRR's only edge here is native directionality; if directional predicates dominate ingest, revisit as a per-type binding, not a wholesale encoder swap.) " % (d, gb) + s)


print("[config] anchor=%s mode=%s Nf=%d blocks=%dx%dx%d M=%d" % (ANCHOR_NAME, RUN_MODE, NF, N_BLOCKS, D_BLOCK, D_BLOCK, M_CODEBOOK), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
