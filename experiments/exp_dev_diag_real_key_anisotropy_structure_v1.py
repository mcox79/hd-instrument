"""DIAGNOSTIC (not a cert cell): characterize the anisotropy STRUCTURE of real LM keys
and test whether the whitening-revival smoke's weak recovery is a RANK-DEFICIENCY artifact
(M<d cov is rank<=M -> shrinkage-ZCA isotropizes noise) vs a genuine real-key anisotropy wall.

Question raised by the whitening smoke FLAG (whitened ~ raw at M=200/400, proj/hidden d=768):
  H1 (rank-deficiency, smoke-only): M<<d -> cov rank<=M -> ZCA whitens null directions -> weak.
       PREDICTION: full M=10k > d=768 -> full-rank cov -> ZCA recovers. Smoke is not the verdict.
  H2 (real anisotropy wall): the anisotropy is low-rank / multi-directional (NOT single common-mode)
       -> mean-center + ZCA cannot isotropize the signal directions -> weak even at M>d.

Discriminator = sweep M across d and watch (a) effective rank PR, (b) common-mode energy fraction,
(c) post-ZCA PR (does isotropization actually take?). pythia-160m hidden=768 so M in {200..2000}
straddles d cleanly. CPU, ~1-2min, no GPU. ASCII only.
"""
import os, sys
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_p = __import__("exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1")
make_facts, encode, _np_norm, fit_zca, apply_zca = _p.make_facts, _p.encode, _p._np_norm, _p.fit_zca, _p.apply_zca
train_contrastive, recall_at = _p.train_contrastive, _p.recall_at

ENCODER = "EleutherAI/pythia-160m"   # hidden=768; structure of anisotropy is a general LM-embedding property
N_KEYS = 2000
M_SWEEP = [200, 400, 768, 1200, 2000]   # straddles d=768 (rank-deficient -> full-rank)
ZCA_TAU = 1e-2


def participation_ratio(eigs):
    """Effective rank PR = (sum l)^2 / sum(l^2). PR/d in [0,1]; 1 = isotropic, low = few-direction."""
    eigs = np.clip(eigs, 0, None)
    s1 = eigs.sum()
    s2 = (eigs ** 2).sum()
    return float(s1 * s1 / s2) if s2 > 0 else 0.0


def structure(X):
    """X: (n, d). Returns anisotropy descriptors of the keys the superposition store would see."""
    n, d = X.shape
    mu = X.mean(0)
    Xc = X - mu
    # total second-moment energy and the fraction carried by the MEAN (common-mode) direction
    e_total = float((X * X).sum() / n)                       # E[||x||^2]
    e_mean = float((mu * mu).sum())                          # ||mu||^2 (single common-mode direction energy)
    cm_frac = e_mean / e_total if e_total > 0 else 0.0
    # centered covariance eigen-spectrum
    cov = (Xc.T @ Xc) / max(n - 1, 1)
    eigs = np.linalg.eigvalsh(cov)[::-1]
    eigs = np.clip(eigs, 0, None)
    pr = participation_ratio(eigs)
    top1 = float(eigs[0] / eigs.sum()) if eigs.sum() > 0 else 0.0
    top5 = float(eigs[:5].sum() / eigs.sum()) if eigs.sum() > 0 else 0.0
    rank_eff = int((eigs > 1e-8 * eigs[0]).sum()) if eigs[0] > 0 else 0
    return dict(d=d, pr=pr, pr_frac=pr / d, cm_frac=cm_frac, top1=top1, top5=top5, rank_eff=rank_eff)


def zca_recovery(X):
    """Apply shrinkage-ZCA (the whitening cell's fix) and report PR before/after on CENTERED keys.
    If ZCA truly isotropizes, post PR_frac -> ~1. In rank-deficient M<d, floored null dirs get
    amplified to noise -> PR_frac stays low / collapses (the smoke regime)."""
    mu, Wz = fit_zca(X, tau=ZCA_TAU)
    Xw = apply_zca(X, mu, Wz)
    cov = np.cov(Xw, rowvar=False)
    eigs = np.clip(np.linalg.eigvalsh(cov)[::-1], 0, None)
    return participation_ratio(eigs) / X.shape[1]


def main():
    print("[diag] encoding %d keys with %s (CPU)..." % (N_KEYS, ENCODER), flush=True)
    _p.ENCODER = ENCODER
    keys, vq = make_facts(N_KEYS)        # CERT591: keys = fact statements (the stored KEY embeddings); index = label
    K = encode(keys).astype(np.float32)
    K = _np_norm(K) * np.sqrt(K.shape[1])     # CERT591 unnormalized-magnitude convention (Ramsauer beta=1/sqrt d)
    d = K.shape[1]
    print("[diag] keys encoded: shape=%s  d=%d" % (K.shape, d), flush=True)
    print()
    print("%-7s | %-8s %-8s %-8s | %-9s %-8s | %-10s" % (
        "M", "PR/d", "cm_frac", "top1", "rank_eff", "regime", "ZCA->PR/d"))
    print("-" * 78)
    for M in M_SWEEP:
        if M > K.shape[0]:
            continue
        Xs = K[:M]
        s = structure(Xs)
        regime = "M<d(rk-def)" if M < d else "M>=d(full)"
        zr = zca_recovery(Xs)
        print("%-7d | %-8.3f %-8.3f %-8.3f | %-9d %-8s | %-10.3f" % (
            M, s["pr_frac"], s["cm_frac"], s["top1"], s["rank_eff"], regime, zr))
    print("-" * 78)
    print()
    # ---- FAITHFUL path: measure rank AFTER CERT591 contrastive projection (what the whitening cell whitens) ----
    PROJ_DIM, TRAIN_M, STEPS = 768, 1500, 200
    g = np.random.default_rng(7)
    keys2, cues2 = make_facts(TRAIN_M + 2000)
    K2 = encode(keys2).astype(np.float32); Q2 = encode(cues2).astype(np.float32)
    perm = g.permutation(len(keys2)); tr, ho = perm[:TRAIN_M], perm[TRAIN_M:]
    print("[diag] training CERT591 contrastive proj (d=%d, train=%d, steps=%d)..." % (PROJ_DIM, TRAIN_M, STEPS), flush=True)
    W = train_contrastive(K2[tr], Q2[tr], PROJ_DIM, STEPS, 7)
    Kp = (K2[ho] @ W).astype(np.float32); Qp = (Q2[ho] @ W).astype(np.float32)
    cal = recall_at(_np_norm(Qp[:500]), _np_norm(Kp[:500]))
    Kp = _np_norm(Kp) * np.sqrt(PROJ_DIM)                  # same Ramsauer-magnitude convention as the store
    sp = structure(Kp); zp = zca_recovery(Kp)
    sr = structure(_np_norm(K2[ho]) * np.sqrt(K2.shape[1]))
    print("  cal(cue->key heldout)=%.3f  (CERT591 ref 0.827)" % cal)
    print("  %-26s | PR/d=%.3f cm_frac=%.3f top1=%.3f top5=%.3f rank_eff=%d" % (
        "RAW keys (d=%d)" % K2.shape[1], sr["pr_frac"], sr["cm_frac"], sr["top1"], sr["top5"], sr["rank_eff"]))
    print("  %-26s | PR/d=%.3f cm_frac=%.3f top1=%.3f top5=%.3f rank_eff=%d" % (
        "CONTRASTIVE-PROJ (d=%d)" % PROJ_DIM, sp["pr_frac"], sp["cm_frac"], sp["top1"], sp["top5"], sp["rank_eff"]))
    print("  CONTRASTIVE-PROJ + shrinkage-ZCA -> PR/d = %.3f  (->1 = isotropized)" % zp)
    print("  [faithful-read] if CONTRASTIVE-PROJ PR/d still LOW and +ZCA does not reach ~1 ->")
    print("                  the whitening cell's INPUT is intrinsically low-rank -> predict ARM1_whitened ~ raw (HARD_FAIL/MIDDLE).")
    print("                  if PR/d HIGH -> proj de-crowds -> whitening could recover; collapse is elsewhere.")
    print()
    print("-" * 78)
    print("[read] cm_frac HIGH (>0.3) => single common-mode dominates -> whitening SHOULD fix.")
    print("[read] cm_frac LOW + PR/d LOW => low-rank multi-direction anisotropy (NOT common-mode).")
    print("[read] ZCA->PR/d jumps to ~1 only where M>=d (full-rank cov); stays low for M<d (rank-def).")
    print("[verdict] if ZCA->PR/d ~1 at M>=d but ~low at M<d => smoke weak-recovery = RANK-DEFICIENCY")
    print("          artifact; full M=10k>d=768 predicted to recover. Else real-key anisotropy wall.")


if __name__ == "__main__":
    main()
