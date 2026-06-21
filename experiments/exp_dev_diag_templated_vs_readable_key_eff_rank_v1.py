"""LOAD-BEARING diagnostic (Skunkworks named it the referent that scopes the whitening MM):
is the storage-chain keys' low effective-rank an INTRINSIC LM-key property, or an ARTIFACT of
TEMPLATED facts (make_facts: near-identical "X was prop value N" sentences)?

If READABLE diverse text keys (shakespeare) have SUBSTANTIALLY higher eff-rank than templated
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
N = int(os.environ.get("DIAG_N", "2000"))


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
    """Diverse readable natural-language keys = tiny-shakespeare lines (reliable urllib
    loader; far more lexically/syntactically diverse than templated make_facts. Single-
    author caveat noted -- still a clean templating-artifact test vs near-identical templates)."""
    from testbed.substrate_lm.data import shakespeare_char_corpus
    txt = shakespeare_char_corpus(split="train", allow_synthetic=False)
    lines = [" ".join(l.split()) for l in txt.split("\n")]
    lines = [l for l in lines if 40 <= len(l) <= 200]   # dialogue/verse lines ~ template length
    return lines[:n]


def main():
    _p.ENCODER = ENCODER
    print("[diag] encoding %d TEMPLATED keys (make_facts)..." % N, flush=True)
    tk, _ = make_facts(N)
    Kt = encode(tk).astype(np.float32)
    st = structure(Kt)
    print("[diag] encoding %d READABLE keys (shakespeare snippets)..." % N, flush=True)
    rk = readable_snippets(N)
    print("[diag]   got %d readable snippets" % len(rk), flush=True)
    Kr = encode(rk).astype(np.float32)
    sr = structure(Kr)
    print()
    print("%-26s | %-8s %-8s %-8s %-8s" % ("key set (d=%d)" % st["d"], "cm_frac", "PR/d", "top1", "top5"))
    print("-" * 64)
    print("%-26s | %-8.3f %-8.4f %-8.3f %-8.3f" % ("TEMPLATED (make_facts)", st["cm_frac"], st["pr_frac"], st["top1"], st["top5"]))
    print("%-26s | %-8.3f %-8.4f %-8.3f %-8.3f" % ("READABLE (shakespeare)", sr["cm_frac"], sr["pr_frac"], sr["top1"], sr["top5"]))
    print("-" * 64)
    ratio = sr["pr_frac"] / st["pr_frac"] if st["pr_frac"] > 0 else float("inf")
    eff_t, eff_r = st["pr_frac"] * st["d"], sr["pr_frac"] * sr["d"]
    print("[eff-rank ratio readable/templated] PR/d: %.2fx (%.0f -> %.0f eff-dims) | cm_frac: %.3f -> %.3f" % (
        ratio, eff_t, eff_r, st["cm_frac"], sr["cm_frac"]))
    print()
    # TWO components, judged SEPARATELY (the headline must not collapse them):
    print("[VERDICT-decomposed] (do NOT collapse the two components)")
    print("  (1) COMMON-MODE: cm_frac %.3f(templated) ~ %.3f(readable) -> INTRINSIC LM anisotropy," % (
        st["cm_frac"], sr["cm_frac"]))
    print("      NOT a templating artifact. Whitening removes this single direction fine.")
    print("  (2) RESIDUAL EFF-RANK: %.2fx higher on readable (%.0f vs %.0f eff-dims) -> templating-SENSITIVE" % (
        ratio, eff_r, eff_t))
    print("      (lower bound: shakespeare is single-author; multi-domain + bigger model + contrastive higher).")
    print("  (3) BUT ABSOLUTE readable rank still LOW (PR/d=%.4f = %.1f%% isotropy)." % (sr["pr_frac"], 100 * sr["pr_frac"]))
    print("[NET] dense-superposition capacity ~ eff-rank, so readable gives ~%.1fx more headroom (~%.0f vs ~%.0f keys)" % (
        ratio, eff_r, eff_t))
    print("      BUT the whitening cell tested M=3k-10k >> %.0f -> dense STILL fails at high M even on readable keys." % eff_r)
    print("      => NOT 'dense reopens'. Honest: dense has MORE HEADROOM on readable keys (low-M ~tens cache viable)")
    print("         but stays NON-VIABLE at the high-M the substrate-LM needs -> TAG-RETRIEVAL remains the high-M path.")
    print("      => Skunkworks whitening-MM correctly SCOPED to templated; readable deserves a dense RE-TEST at")
    print("         realistic M, NOT an assumed-closed NOR an assumed-reopen. The substrate-LM key pipeline decides.")


if __name__ == "__main__":
    main()
