"""LOAD-BEARING diagnostic (Skunkworks named it the referent that scopes the whitening MM):
is the storage-chain keys' low effective-rank an INTRINSIC LM-key property, or an ARTIFACT of
TEMPLATED facts (make_facts: near-identical "X was prop value N" sentences)?

If READABLE diverse text keys (20newsgroups) have SUBSTANTIALLY higher eff-rank than templated
keys -> the rank-1/anisotropy trap that killed whitening is a TEMPLATING ARTIFACT -> dense
superposition is NOT closed for the real substrate-native-LM use-case (readable-text keys) ->
REOPENS dense. If readable keys are SIMILARLY low-rank -> intrinsic -> dense stays closed, and
M1 must use tag-retrieval from the start.

Raw-key comparison (no contrastive proj -- avoids the CPU-untrainable-proj confound; the raw
eff-rank IS the load-bearing geometric property). pythia-160m, CPU. ASCII only.
"""
import os, sys
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_p = __import__("exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1")
make_facts, encode, _np_norm = _p.make_facts, _p.encode, _p._np_norm

ENCODER = "EleutherAI/pythia-160m"
N = 2000


def participation_ratio(eigs):
    eigs = np.clip(eigs, 0, None); s1 = eigs.sum(); s2 = (eigs ** 2).sum()
    return float(s1 * s1 / s2) if s2 > 0 else 0.0


def structure(K):
    """K: (n, d) raw embeddings. Returns common-mode + effective-rank descriptors."""
    K = _np_norm(K) * np.sqrt(K.shape[1])              # CERT591 magnitude convention
    n, d = K.shape
    mu = K.mean(0); e_total = float((K * K).sum() / n); e_mean = float((mu * mu).sum())
    cm_frac = e_mean / e_total if e_total > 0 else 0.0  # = mean pairwise cosine (single common-mode energy)
    Xc = K - mu; cov = (Xc.T @ Xc) / max(n - 1, 1)
    eigs = np.clip(np.linalg.eigvalsh(cov)[::-1], 0, None)
    pr = participation_ratio(eigs)
    top1 = float(eigs[0] / eigs.sum()) if eigs.sum() > 0 else 0.0
    top5 = float(eigs[:5].sum() / eigs.sum()) if eigs.sum() > 0 else 0.0
    return dict(d=d, pr=pr, pr_frac=pr / d, cm_frac=cm_frac, top1=top1, top5=top5)


def readable_snippets(n):
    from sklearn.datasets import fetch_20newsgroups
    data = fetch_20newsgroups(subset="train", remove=("headers", "footers", "quotes"))
    out = []
    for t in data.data:
        t = " ".join(t.split())
        if len(t) < 40:
            continue
        out.append(t[:120])                            # ~match templated-fact length (short statements)
        if len(out) >= n:
            break
    return out


def main():
    _p.ENCODER = ENCODER
    print("[diag] encoding %d TEMPLATED keys (make_facts)..." % N, flush=True)
    tk, _ = make_facts(N)
    Kt = encode(tk).astype(np.float32)
    st = structure(Kt)
    print("[diag] encoding %d READABLE keys (20newsgroups snippets)..." % N, flush=True)
    rk = readable_snippets(N)
    print("[diag]   got %d readable snippets" % len(rk), flush=True)
    Kr = encode(rk).astype(np.float32)
    sr = structure(Kr)
    print()
    print("%-26s | %-8s %-8s %-8s %-8s" % ("key set (d=%d)" % st["d"], "cm_frac", "PR/d", "top1", "top5"))
    print("-" * 64)
    print("%-26s | %-8.3f %-8.4f %-8.3f %-8.3f" % ("TEMPLATED (make_facts)", st["cm_frac"], st["pr_frac"], st["top1"], st["top5"]))
    print("%-26s | %-8.3f %-8.4f %-8.3f %-8.3f" % ("READABLE (20newsgroups)", sr["cm_frac"], sr["pr_frac"], sr["top1"], sr["top5"]))
    print("-" * 64)
    ratio = sr["pr_frac"] / st["pr_frac"] if st["pr_frac"] > 0 else float("inf")
    print("[eff-rank ratio readable/templated] PR/d: %.2fx  | cm_frac drop: %.3f -> %.3f" % (
        ratio, st["cm_frac"], sr["cm_frac"]))
    print()
    if ratio >= 3.0 or sr["pr_frac"] >= 0.15:
        print("[VERDICT] READABLE keys are SUBSTANTIALLY higher eff-rank (%.2fx, PR/d=%.4f)." % (ratio, sr["pr_frac"]))
        print("          => the low-rank that killed whitening is largely a TEMPLATING ARTIFACT.")
        print("          => dense superposition is NOT closed for readable-text keys -> REOPENS dense")
        print("             for the substrate-native-LM use-case. Skunkworks's MM stays scoped-to-templated.")
    elif ratio <= 1.5:
        print("[VERDICT] READABLE keys are SIMILARLY low-rank (%.2fx, PR/d=%.4f)." % (ratio, sr["pr_frac"]))
        print("          => the low-rank is INTRINSIC to LM mean-pooled keys, NOT a templating artifact.")
        print("          => dense superposition stays CLOSED; M1 must use TAG-RETRIEVAL from the start.")
    else:
        print("[VERDICT] PARTIAL: readable keys moderately higher-rank (%.2fx, PR/d=%.4f)." % (ratio, sr["pr_frac"]))
        print("          => templating contributes but does not fully explain; dense marginal on readable keys.")
    print("[note] raw keys; mean-pooled pythia-160m. Higher-capacity/larger models + contrastive de-crowd")
    print("       would shift absolute PR/d up; the TEMPLATED-vs-READABLE RATIO is the load-bearing signal.")


if __name__ == "__main__":
    main()
